from arches_inclusion_rule.models import InclusionRule

# TODO: implement - could this interface to the existing work sufficiently?
class QuerySetRule(InclusionRule):
    class Meta:
        proxy = True

    @classmethod
    def do_get_search_rule_url(self, inclusion_rule):
        return False
