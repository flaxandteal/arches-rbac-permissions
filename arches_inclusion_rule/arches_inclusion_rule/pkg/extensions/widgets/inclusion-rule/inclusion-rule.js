import ko from 'knockout';
import InclusionRuleSelectViewModel from 'arches_inclusion_rule/arches_inclusion_rule/media/js/viewmodels/inclusion-rule-select';
import inclusionRuleTemplate from 'templates/views/components/widgets/inclusion-rule.htm';
import 'bindings/select2-query';

const viewModel = function(params) {
    params.configKeys = ['defaultValue'];
    InclusionRuleSelectViewModel.apply(this, [params]);

    var defaultValue = ko.unwrap(this.defaultValue);
    var self = this;

    if (self.configForm){
        self.select2Config.value = self.defaultValue;
    }
};

export default ko.components.register('inclusion-rule', {
    viewModel: viewModel,
    template: inclusionRuleTemplate,
});
