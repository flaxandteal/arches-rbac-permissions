import ko from 'knockout';
import UserSelectViewModel from 'viewmodels/user-select';
import userTemplate from 'templates/views/components/widgets/user.htm';
import 'bindings/select2-query';


const viewModel = function(params) {
    params.configKeys = ['defaultValue'];
    UserSelectViewModel.apply(this, [params]);

    var defaultValue = ko.unwrap(this.defaultValue);
    var self = this;

    if (self.configForm){
        self.select2Config.value = self.defaultValue;
    }
};

export default ko.components.register('user', {
    viewModel: viewModel,
    template: userTemplate,
});
