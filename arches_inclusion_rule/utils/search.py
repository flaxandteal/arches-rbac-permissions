from datetime import datetime
from django.utils.translation import gettext as _
from elasticsearch.client import TasksClient
from elasticsearch.exceptions import RequestError
from arches.app.search.components.base import SearchFilterFactory
from arches.app.search.elasticsearch_dsl_builder import Dsl, Query
from arches.app.search.search import SearchEngine
from typing import List, Tuple, Any
from types import SimpleNamespace

class UpdateByQueryDSLException(Exception):
    pass

class CommandSearchFilterFactory(SearchFilterFactory):
    def __init__(self, key_value_pairs: List[Tuple[str, Any]]):
        self.key_value_pairs = key_value_pairs

        # TODO: this is awful, but the only other way to resolve the deep-accesses
        # of request is to patch the architecture for sep of concerns (as we did in Coral)
        # Does the database layer needs to have a request with a user, or is there a way to improve that?
        user = SimpleNamespace(is_superuser=True, groups=[], is_authenticated=True, id=None, has_perm=lambda *args: True)
        mock_request = SimpleNamespace(GET={}, POST={}, user=user, method="POST")
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


class UpdatingSearchEngine(SearchEngine):
    def update_by_query(self, **kwargs):
        """
        Update items by a search in the index.
        Pass an index and id (or list of ids) to get a specific document(s)
        Pass a query with a query dsl to perform a search

        """

        kwargs = self._add_prefix(**kwargs)
        query = kwargs.get("query", None)
        script = kwargs.get("script", None)

        if query is None or script is None:
            message = "%s: WARNING: update-by-query missing query or script" % (datetime.now())
            self.logger.exception(message)
            raise RuntimeError(message)

        ret = None
        try:
            print(kwargs)
            ret = self.es.update_by_query(**kwargs).body
        except RequestError as detail:
            self.logger.exception("%s: WARNING: update-by-query failed for query: %s \nException detail: %s\n" % (datetime.now(), query, detail.info))
        return ret

    def make_tasks_client(self):
        return TasksClient(self.es)
