import ko from 'knockout';
import _ from 'underscore';
import uuid from 'uuid';
import dispose from 'utils/dispose';
import $ from 'jquery';
import arches from 'arches';
import WidgetViewModel from 'viewmodels/widget';

import { generateArchesURL } from "@/arches/utils/generate-arches-url.ts";

// TODO: sort out translation string removal, as otherwise cannot cancel editing
// (as translating group names does not make sense)

var NAME_LOOKUP = {};
var GroupSelectViewModel = function(params) {
    // TODO: tidy up to remove excess settings
    // Getting this to display was a _long_ journey.
    var self = this;

    // TODO: not sure where this is _not_ being set for this widget, but is for others.
    if (params.value && !ko.isObservable(params.value)) {
        params.value = ko.observable(params.value);
    }

    const url_get_group_names_all = generateArchesURL(
        "get_group_names_all"
    );

    const url_get_group_names_one = generateArchesURL(
        "get_group_names_one"
    );

    params.configKeys = ['placeholder', 'defaultValue'];

    this.allowClear = params.allowClear ?? true;
    this.displayName = ko.observable('');
    this.selectedItem = params.selectedItem || ko.observable();
    this.formData = params.formData || null;
    this.form = params.form || null;
    this.tile = params.tile || null;
    this.widget = params.widget || null;
    this.value = params.value || ko.observable(null);
    this.configForm = params.configForm || false;
    this.configKeys = params.configKeys || [];
    this.configKeys.push('label');
    this.configKeys.push('required');
    this.state = params.state || 'form';
    this.hideEmptyNodes = params.hideEmptyNodes;
    this.externalObservables = ['value', 'config', 'expanded', 'defaultValueSubscription', 'valueSubscription'];
    var self = this;
    this.state = params.state || 'form';
    var expanded = params.expanded || ko.observable(false);
    var nodeid = params.node ? params.node.nodeid : uuid.generate();
    this.expanded = ko.computed({
        read: function() {
            return nodeid === expanded();
        },
        write: function(val) {
            if (val) {
                expanded(nodeid);
            } else {
                expanded(false);
            }
        }
    });
    this.value = params.value || ko.observable(null);
    this.formData = params.formData || null;
    this.form = params.form || null;
    this.tile = params.tile || null;
    this.widget = params.widget || null;
    this.inResourceEditor = (typeof params.inResourceEditor === "boolean" ? params.inResourceEditor : null);
    this.results = params.results || null;
    this.disabled = params.disabled || ko.observable(false);
    this.node = params.node || null;
    this.configForm = params.configForm || false;
    this.config = params.config || ko.observable({});
    this.configObservables = params.configObservables || {};
    this.configKeys = params.configKeys || [];
    this.configKeys.push('label');
    this.configKeys.push('required');
    if (this.node) {
        this.required = this.node.isrequired;
    }
    if (typeof this.config !== 'function') {
        this.config = ko.observable(this.config);
    }

    this.disposables = [];

    var subscribeConfigObservable = function(obs, key) {
        self[key] = obs;

        var forwardSubscription = self[key].subscribe(function(val) {
            if (params.hasOwnProperty('graphDesignerHasDirtyWidget')) {
                if (val && val !== params.config()[key]) {
                    params.graphDesignerHasDirtyWidget(true);
                }
            }

            var configObj = self.config();
            configObj[key] = val;
            self.config(configObj);
        });

        var reverseSubscription = self.config.subscribe(function(val) {
            if (val[key] !== self[key]()) {
                self[key](val[key]);
            }
        });
        self.disposables.push(forwardSubscription);
        self.disposables.push(reverseSubscription);
    };
    _.each(this.configObservables, subscribeConfigObservable);
    _.each(this.configKeys, function(key) {
        var obs = ko.observable(self.config()[key]);
        subscribeConfigObservable(obs, key);
    });

    if (ko.isObservable(this.value) && ko.isObservable(this.defaultValue)) {
        var defaultValue = this.defaultValue();
        if (this.tile && !this.tile.noDefaults && !ko.unwrap(this.tile.dirty) && ko.unwrap(this.tile.tileid) == "" && defaultValue != null && defaultValue != "") {
            this.value(defaultValue);
        }

        if (!self.form) {
            if (ko.isObservable(self.value)) {
                self.valueSubscription = self.value.subscribe(function(val){
                    if (self.defaultValue() != val) {
                        self.defaultValue(val);
                    }
                });
                self.defaultValueSubscription = self.defaultValue.subscribe(function(val){
                    if (self.value() != val) {
                        self.value(val);
                    }
                });
            }
        }
    }

    this.disposables.push(this.defaultValueSubscription);
    this.disposables.push(this.valueSubscription);

    this.onInit = params.onInit;
    if (typeof this.onInit === 'function') {
        this.onInit();
    }

    this.dispose = function(){
        dispose(self);
    };

    this.nodeCssClasses = ko.pureComputed(function() {
        return [ko.unwrap(self.node?.alias),
            self.node?.graph?.attributes?.slug,
            self.widget?.widgetLookup[ko.unwrap(self.widget?.widget_id)].name
            ].join(" ").trim();
    });

    const resourceId = (this.tile && this.tile.resourceinstance_id) || (params && params.resourceinstance_id) || null;

    this.displayValue = ko.computed(function() {
        var name = self.displayName();
        var displayVal = null;

        if (name) {
            displayVal = name;
        }

        return displayVal;
    });

    this.setName = function() {
        const val = self.value();
        if (ko.unwrap(val)) {
            const value = parseInt(ko.unwrap(ko.unwrap(val).groupId));
            if (!isNaN(value)) {
                if (NAME_LOOKUP[value]) {
                    self.displayName(NAME_LOOKUP[value]);
                } else {
                    $.ajax(url_get_group_names_one + '?groupid=' + ko.unwrap(value), {
                        dataType: "json"
                    }).done(function(data) {
                        NAME_LOOKUP[data.id] = data.text;
                        self.displayName(data.text);
                    });
                }
            }
        }
    };
    this.setName();

    this.groupToAdd = ko.observable(null);
    this.groupToAdd.subscribe(function(data) {
        let valueInt;
        if (data && typeof data === 'object' && data.groupId) {
            valueInt = parseInt(ko.unwrap(data.groupId));
        } else if (data) {
            valueInt = data;
        }
        if (valueInt) {
            self.value({
                "groupId": ko.unwrap(valueInt),
            });
        }
    });
    this.value.subscribe(function(val) {
        if (val) {
            self.groupToAdd(val.groupId);
        } else {
            self.groupToAdd(null);
        }
        self.setName();
    });

    this.select2Config = {
        value: self.groupToAdd,
        clickBubble: true,
        multiple: false,
        closeOnSelect: true,
        placeholder: self.placeholder,
        allowClear: self.allowClear,
        ajax: {
            url: url_get_group_names_all,
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
            var val = self.value();
            
            var setSelectionData = function(data) {
                let valueData;
                let valueInt;
                if (data && typeof data === 'object' && data.groupId) {
                    valueInt = parseInt(ko.unwrap(data.groupId));
                } else {
                    valueInt = data;
                }
                if (valueInt) {
                    valueData = {
                        id: valueInt,
                        text: NAME_LOOKUP[valueInt],
                    };
                } else {
                    console.warn("Could not load value", valueId);
                }

                if(!self.select2Config.initComplete && valueData){
                    var option = new Option(valueData.text, valueData.id, true, true);
                    $(el).append(option);
                    self.select2Config.initComplete = true;
                }
                callback(valueData);
                self.value({
                    groupId: ko.unwrap(valueData.id)
                });
            };

            const value = parseInt(ko.unwrap(ko.unwrap(val).groupId));
            if (ko.unwrap(value)) {
                if (NAME_LOOKUP[value]) {
                    setSelectionData(value);
                } else {
                    $.ajax(url_get_group_names_one + '?groupid=' + ko.unwrap(value), {
                        dataType: "json"
                    }).done(function(data) {
                        NAME_LOOKUP[value] = data.text;
                        setSelectionData(value);
                    });
                }
            }

        },
        onSelect: function(item) {
            self.selectedItem(item);
            var ret = {
                groupId: ko.unwrap(item.id),
            };
            self.value(ret);
        }
    };
};

export default GroupSelectViewModel;
