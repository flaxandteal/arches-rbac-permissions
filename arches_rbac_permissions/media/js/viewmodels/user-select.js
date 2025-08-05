import ko from 'knockout';
import $ from 'jquery';
import arches from 'arches';
import WidgetViewModel from 'viewmodels/widget';

import { generateArchesURL } from "@/arches/utils/generate-arches-url.ts";

// TODO: sort out translation string removal, as otherwise cannot cancel editing
// (as translating usernames does not make sense)

var NAME_LOOKUP = {};
var UserSelectViewModel = function(params) {
    var self = this;

    const url_get_user_names_all = generateArchesURL(
        "get_user_names_all"
    );

    const url_get_user_names_one = generateArchesURL(
        "get_user_names_one"
    );

    params.configKeys = ['placeholder', 'defaultValue'];

    this.multiple = params.multiple || false;
    this.allowClear = params.allowClear ?? true;
    this.displayName = ko.observable('');

    WidgetViewModel.apply(this, [params]);

    this.valueList = ko.computed(function() {
        var valueList = self.value() || self.defaultValue();
        self.displayName();
        
        if (Array.isArray(valueList)) {
            return valueList;
        } else if (!self.multiple && valueList) {
            return [valueList];
        }
        return [];
    });

    this.valueObjects = ko.computed(function() {
        self.displayName();
        return self.valueList().map(function(value) {
            const valueId = parseInt(value);
            return {
                id: valueId,
                name: NAME_LOOKUP[valueId]
            };
        }).filter(function(item) {
            return item.name;
        });
    });

    this.displayValue = ko.computed(function() {
        var val = self.value();
        var name = self.displayName();
        var displayVal = null;

        if (val) {
            displayVal = name;
        }

        return displayVal;
    });

    this.setNames = function() {
        var names = [];
        self.valueList().forEach(function(val) {
            if (ko.unwrap(val)) {
                if (NAME_LOOKUP[val]) {
                    names.push(NAME_LOOKUP[val]);
                    self.displayName(names.join(', '));
                } else {
                    $.ajax(url_get_user_names_one + '?userid=' + ko.unwrap(val), {
                        dataType: "json"
                    }).done(function(data) {
                        NAME_LOOKUP[data.id] = data.text;
                        names.push(data.text);
                        self.displayName(names.join(', '));
                    });
                }
            }
        });
    };
    this.setNames();

    this.value.subscribe(function() {
        self.setNames();
    });

    this.select2Config = {
        value: self.value,
        clickBubble: true,
        multiple: self.multiple,
        closeOnSelect: true,
        placeholder: self.placeholder,
        allowClear: self.allowClear,
        ajax: {
            url: url_get_user_names_all,
            dataType: 'json',
            quietMillis: 250,
            data: function(requestParams) {
                let term = requestParams.term || '';
                let page = requestParams.page || 1;
                return {
                    query: term,
                    page: page,
                };
            },
            processResults: function(data) {
                return {
                    "results": data.results,
                    "pagination": {
                        "more": data.more
                    }
                };
            }
        },
        templateResult: function(item) {
            var indentation = '';
            for (var i = 0; i < item.depth-1; i++) {
                indentation += '&nbsp;&nbsp;&nbsp;&nbsp;';
            }
            return indentation + item.text;
        },
        templateSelection: function(item) {
            return item.text;
        },
        escapeMarkup: function(m) { return m; },
        initComplete: false,
        initSelection: function(el, callback) {
            var valueList = self.valueList();
            
            var setSelectionData = function(data) {
                var valueData = [];

                if (self.multiple || Array.isArray(valueList)) {
                    if (!(data instanceof Array)) { data = [data]; }
                    
                    valueData = data.map(function(valueId) {
                        const valueInt = parseInt(valueId);
                        return {
                            id: valueInt,
                            text: NAME_LOOKUP[valueInt],
                        };
                    });

                    /* add the rest of the previously selected values */ 
                    valueList.forEach(function(value) {
                        if (value !== valueData[0].id) {
                            valueData.push({
                                id: value,
                                text: NAME_LOOKUP[value],
                            });
                        }
                    });

                    /* keeps valueData obeying valueList as ordering source of truth */ 
                    if (valueData[0].id !== valueList[0]) {
                        valueData.reverse();
                    }
                } else {
                    const valueId = parseInt(data);
                    valueData = [{
                        id: valueId,
                        text: NAME_LOOKUP[valueId],
                    }];
                }
                if(!self.select2Config.initComplete){
                    valueData.forEach(function(data) {
                        var option = new Option(data.text, data.id, true, true);
                        $(el).append(option);
                    });
                    self.select2Config.initComplete = true;
                }
                callback(valueData);
            };

            if (valueList.length > 0) {
                valueList.forEach(function(val) {
                    const value = parseInt(val);
                    if (ko.unwrap(value)) {
                        if (NAME_LOOKUP[value]) {
                            setSelectionData(value);
                        } else {
                            $.ajax(url_get_user_names_one + '?userid=' + ko.unwrap(value), {
                                dataType: "json"
                            }).done(function(data) {
                                NAME_LOOKUP[value] = data.text;
                                setSelectionData(value);
                            });
                        }
                    }
                });
            }else{
                callback([]);
            }


        }
    };
    this.select2ConfigMulti = { ...this.select2Config };
    this.select2ConfigMulti.multiple = true;
};

export default UserSelectViewModel;
