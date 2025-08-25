import { generateArchesURL } from "@/arches/utils/generate-arches-url.ts";
import $ from 'jquery';
import ko from 'knockout';
import arches from 'arches';
import savedSearchesTemplate from 'templates/views/components/search/saved-searches.htm';
import 'bindings/smartresize';


const componentName = 'saved-searches';
const viewModel = function(sharedStateObject) {
    var self = this;
    self.searchFilterVms = sharedStateObject.searchFilterVms;
    this.query = sharedStateObject.query;
    console.log(this.query, 'query');
    this.savedSearchName = ko.observable();
    this.result = ko.observable();
    const url_saved_searches = generateArchesURL(
        "savedsearches"
    );

    this.executeSave = function(){
        var payload = {
            "query": JSON.stringify(ko.unwrap(self.query)),
            "savedSearchName": this.savedSearchName() || "Saved Search"
        };
        console.log(payload);
        $.ajax({
            type: "POST",
            url: url_saved_searches,
            data: payload
        }).done(function(response) {
            self.result(response.message);
        });
    };

        
    self.urls = arches.urls;
    self.selectedPopup = sharedStateObject.selectedPopup;
    self.items = ko.observableArray([]);
    self.personalItems = ko.observableArray([]);

    $.ajax({
        type: "GET",
        url: url_saved_searches
    }).done(function(response) {
        response.forEach(function(search) {
            const parts = []
            for (const [key, value] of Object.entries(search.query)) {
                parts.push(encodeURIComponent(key) + '=' + encodeURIComponent(value));
            }
            let url = generateArchesURL("search_home") + "?" + parts.join("&");
            console.log(url, 'url', search.query, search, parts);
            self.personalItems.push({
                image: undefined,
                title: search.name,
                searchUrl: url
            });
        });
    });

    $.ajax({
        type: "GET",
        url: arches.urls.api_search_component_data + componentName,
        context: this
    }).done(function(response) {
        response[componentName].forEach(function(search) {
            let searchImageUrl = arches.urls.url_subpath + ((search.IMAGE && search.IMAGE.length > 0) ? search.IMAGE[0].url : '');
            searchImageUrl = searchImageUrl.replace('//', '/');
            self.items.push({
                image: searchImageUrl,
                title: search.SEARCH_NAME ? search.SEARCH_NAME[arches.activeLanguage].value : "",
                subtitle: search.SEARCH_DESCRIPTION ? search.SEARCH_DESCRIPTION[arches.activeLanguage].value : "",
                searchUrl: search.SEARCH_URL ? search.SEARCH_URL[arches.activeLanguage].value: ""
            });
        });
    });
    self.searchFilterVms[componentName](self);

    self.options = {
        itemSelector: '.ss-grid-item',
        masonry: {
            columnWidth: 500,
            gutterWidth: 25,
        }
    };
};

export default ko.components.register(componentName, {
    viewModel: viewModel,
    template: savedSearchesTemplate,
});
