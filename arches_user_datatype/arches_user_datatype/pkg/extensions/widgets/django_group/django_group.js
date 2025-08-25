import ko from 'knockout';
import DjangoGroupSelectViewModel from 'arches_user_datatype/arches_user_datatype/media/js/viewmodels/django-group-select';
import djangoGroupTemplate from 'templates/views/components/widgets/django-group.htm';
import 'bindings/select2-query';

const viewModel = function(params) {
    params.configKeys = ['defaultValue'];
    DjangoGroupSelectViewModel.apply(this, [params]);

    var defaultValue = ko.unwrap(this.defaultValue);
    var self = this;

    if (self.configForm){
        self.select2Config.value = self.defaultValue;
    }
};

export default ko.components.register('django-group', {
    viewModel: viewModel,
    template: djangoGroupTemplate,
});
