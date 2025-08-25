import json
from django.urls import reverse
from urllib.parse import quote, urlencode
from arches_inclusion_rule.models import InclusionRule

# TODO: Can we always (in any rule) just act as a proxy model for IR?
# TODO: The goal would be to merge SearchRule and QuerySetRule, but feature parity seems
# unlikely before Arches 9, and rule definition has been a blocker for some time, so this
# allows a stepped transition instead of rushing it
class SearchRule(InclusionRule):
    class Meta:
        proxy = True

    @classmethod
    def do_get_search_rule_url(cls, inclusion_rule):
        filters = {
            key: json.dumps(value) for key, value in inclusion_rule.definition.items()
        }
        return f"{reverse('search_home')}?{urlencode(filters, quote_via=quote)}"
        # We cannot use Django urlencode because it maps space to + in JSON
