from django.utils.translation import gettext as _
from arches.app.search.components.base import SearchFilterFactory
from arches.app.search.elasticsearch_dsl_builder import Dsl, Query
from typing import List, Tuple, Any
from types import SimpleNamespace

class UpdateByQueryDSLException(Exception):
    pass

class CommandSearchFilterFactory(SearchFilterFactory):
    def __init__(self, key_value_pairs: List[Tuple[str, Any]]):
        self.key_value_pairs = key_value_pairs

        # TODO: this is awful, but the only other way to resolve the deep-accesses
        # of request is to patch the architecture for sep of concerns (as we did in Coral)
        user = SimpleNamespace(is_superuser=True)
        mock_request = SimpleNamespace(GET={}, POST={}, user=user)
        super().__init__(request=mock_request, user=user)

    def create_search_query_dict(self, _: List[Tuple[str, Any]]):
        # handles list of key,value tuples so that dict-like data from POST and GET
        # requests can be concatenated into single method call
        searchview_component_name = self.get_searchview_name()
        searchview_instance = self.get_filter(searchview_component_name)
        return searchview_instance.create_query_dict(dict(self.key_value_pairs))

class UpdateByQuery(Dsl):
    def __init__(self, se, **kwargs):
        self.se = se
        self.query = kwargs.pop("query", Query(se))
        self.script = kwargs.pop("script", None)
        if self.query is None:
            raise UpdateByQueryDSLException(_('You need to specify a "query"'))
        if self.script is None:
            raise UpdateByQueryDSLException(_('You need to specify a "script"'))


    def run(self, index="", **kwargs):
        self.query.prepare()
        self.dsl = {
            "query": self.query.dsl["query"],
            "script": self.script
        }
        self.dsl.update(kwargs)
        return self.se.update_by_query(index=index, **self.dsl)

