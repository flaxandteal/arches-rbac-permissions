"""Unit tests for SearchRule URL construction.

``SearchRule.do_get_search_rule_url`` rebuilds the Arches search-page URL from a
saved rule definition. It deliberately avoids ``django.utils.http.urlencode``
because that maps spaces to ``+``, which corrupts the JSON-encoded filter values
(see the comment in the source).
"""

import json
from types import SimpleNamespace
from urllib.parse import parse_qs, urlsplit

from django.urls import reverse

from arches_inclusion_rule.rules.search_rule import SearchRule


def _url(definition):
    # do_get_search_rule_url only reads `.definition`, so a stand-in avoids
    # needing a saved model instance / database.
    return SearchRule.do_get_search_rule_url(SimpleNamespace(definition=definition))


def test_points_at_the_search_home_view():
    assert _url({}).startswith(reverse("search_home"))


def test_filter_values_are_json_encoded():
    value = [{"graphid": "717291c0-99cc-4aa0-98c1-b37cc21a8a3a", "name": "Book"}]
    query = urlsplit(_url({"resource-type-filter": value})).query
    decoded = parse_qs(query)["resource-type-filter"][0]
    assert json.loads(decoded) == value


def test_spaces_are_percent_encoded_not_plus():
    query = urlsplit(_url({"term-filter": "Ian McDonald"})).query
    assert "%20" in query
    assert "+" not in query
