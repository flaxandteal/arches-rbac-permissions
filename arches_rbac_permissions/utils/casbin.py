import hashlib
import time
import uuid
import json
import logging
from functools import partial
from urllib.parse import parse_qs
from arches.app.search.components.base import SearchFilterFactory
from arches.app.search.elasticsearch_dsl_builder import Bool, Match, Query, Ids, Nested, Terms, MaxAgg, Aggregation
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.mappings import RESOURCES_INDEX
from arches.app.models.models import Plugin
from arches.app.models.resource import Resource
from arches_querysets.models import ResourceTileTree, GraphWithPrefetching
from arches_rbac_permissions.models import InclusionRule

from .search import CommandSearchFilterFactory, UpdateByQuery

logger = logging.getLogger(__name__)

def _consistent_hash(string: str):
    hsh = hashlib.sha256(string.encode("utf-8"))
    return uuid.UUID(hsh.hexdigest()[::2])

class SetApplicator:
    def __init__(self, print_statistics, wait_for_completion, synchronous=False):
        self.print_statistics = print_statistics
        self.wait = wait_for_completion and (not synchronous)
        if synchronous:
            print("""
                WARNING: synchronous currently 409s due to a
                limitation of Elasticsearch:
                  https://stackoverflow.com/questions/56602137/wait-for-completion-of-updatebyquery-with-the-elasticsearch-dsl
                This may still be useful for debugging purposes.
                TODO: use the lower-level refresh API for passing retry_on_conflict.
            """)
        self.synchronous = synchronous

    def _apply_set(self, se, set_id, set_query, resourceinstanceid=None):
        results = []
        for add_not_remove in (True, False):
            dsl = Query(se=se)
            bool_query = Bool()
            if resourceinstanceid:
                bool_query.must(Ids(ids=[str(resourceinstanceid)]))
            if add_not_remove:
                bool_query.must_not(set_query().dsl["query"])
                bool_query.must(Nested(path="permissions", query=Terms(field="permissions.sets", terms=[str(set_id)])))
                sets = [str(set_id)]
                source = """
                if (ctx._source.sets != null) {
                    for (int i=ctx._source.sets.length-1; i>=0; i--) {
                        if (params.logicalSets.contains(ctx._source.sets[i].id)) {
                            ctx._source.sets.remove(i);
                        }
                    }
                }
                """
            else:
                bool_query.must(set_query().dsl["query"])
                bool_query.must_not(Nested(path="permissions", query=Terms(field="permissions.sets", terms=[str(set_id)])))
                source = """
                if (ctx._source.permissions.sets == null) {
                    ctx._source.permissions.sets = [];
                }
                ctx._source.permissions.sets.addAll(params.logicalSets);
                """
                sets = [str(set_id)]
            dsl.add_query(bool_query)
            update_by_query = UpdateByQuery(se=se, query=dsl, script={
                "lang": "painless",
                "source": source,
                "params": {
                    "logicalSets": sets
                }
            })
            results.append(update_by_query.run(index=RESOURCES_INDEX, wait_for_completion=self.synchronous))
        return results

    def apply_sets(self, resourceinstanceid=None):
        """Apply set mappings to resources.

        Run update-by-queries to mark/unmark sets against resources in Elasticsearch.
        """

        # TODO: leaving Plugins out for now
        # print("Confirming all plugins present")
        # plugins = {str(plugin.pk): plugin for plugin in Plugin.objects.all()}
        # plugins.update({str(plugin.slug): plugin for plugin in plugins.values()})
        # arches_plugins = ArchesPlugin.all()
        # for ap in arches_plugins:
        #     if ap.plugin_identifier and ap.id != _consistent_hash(ap.plugin_identifier):
        #         print("Found a plugin with an incorrect identifier - removing", ap.plugin_identifier, ap.id)
        #         ap.delete()
        # arches_plugins = ArchesPlugin.all()
        # known_plugins = set(str(plugins[str(plugin.plugin_identifier)].pk) for plugin in arches_plugins)
        # known_plugins |= set(str(plugins[str(plugin.plugin_identifier)].slug) for plugin in arches_plugins)
        # print(known_plugins)

        # unknown_plugins = set(str(plugin.pk) for plugin in Plugin.objects.all()) - known_plugins
        # print(unknown_plugins, "UP")
        # for plugin in unknown_plugins:
        #     plugin = Plugin.objects.get(pk=plugin)
        #     ap = ArchesPlugin()
        #     ap.name = str(plugin.name) or "(unknown)"
        #     ap.plugin_identifier = str(plugin.slug or plugin.pk)
        #     ap.id = _consistent_hash(ap.plugin_identifier)
        #     ap.save()
        #     ap._.index()

        # print("Done with plugins")

        from arches.app.search.search_engine_factory import SearchEngineInstance as _se

        try:
            logical_sets = ResourceTileTree.get_tiles(graph_slug="logical_set")
        except GraphWithPrefetching.DoesNotExist:
            logger.error("Logical Set not loaded yet")
            return
        results = []
        print("Print statistics?", self.print_statistics)
        for logical_set in logical_sets:
            logical_set_data = logical_set.aliased_data
            if logical_set_data.member_definition:
                # user=True is shorthand for "do not restrict by user"
                print(logical_set_data.member_definition.aliased_data.member_definition)
                member_definition = logical_set_data.member_definition.aliased_data.member_definition
                if not member_definition or not (inclusion_rule_id := member_definition.get("inclusionRuleId")):
                    logger.error("Could not find the inclusion rule %s for logical set %s", str(inclusion_rule_id), str(logical_set.pk))
                    continue
                ir = InclusionRule.objects.get(pk=inclusion_rule_id)

                if not ir.classname == "SearchRule":
                    logger.error("QuerySets are not yet supported, in the rule %s for logical set %s", str(inclusion_rule_id), str(logical_set.pk))
                    continue
                parameters = ir.definition
                print(parameters)
                for key, value in parameters.items():
                    if len(value) != 1:
                        raise RuntimeError("Each filter type must appear exactly once")
                    parameters[key] = json.dumps(value)
                print(parameters)
                def _logical_set_query(parameters):
                    search_filter_factory = CommandSearchFilterFactory(parameters)
                    searchview_component_instance = search_filter_factory.get_searchview_instance()
                    _, inner_dsl = (
                        searchview_component_instance.handle_search_results_query(
                            search_filter_factory, returnDsl=True
                        )
                    )
                    return inner_dsl["query"]
                logical_set_query = partial(_logical_set_query, parameters)
                if self.print_statistics:
                    count = logical_set_query().count(index=RESOURCES_INDEX)
                    print("Logical Set:", logical_set.pk)
                    print("Definition:", logical_set_data.member_definition)
                    print("Count:", count)
                results = self._apply_set(_se, f"l:{logical_set.pk}", logical_set_query, resourceinstanceid=resourceinstanceid)
                if self.wait:
                    self.wait_for_completion(_se, results)
                if self.print_statistics:
                    dsl = Query(se=_se)
                    bool_query = Bool()
                    bool_query.must(Nested(path="permissions", query=Terms(field="permissions.sets", terms=[f"l:{logical_set.pk}"])))
                    if resourceinstanceid:
                        bool_query.must(Ids(ids=[str(resourceinstanceid)]))
                    dsl.add_query(bool_query)
                    count = dsl.count(index=RESOURCES_INDEX)
                    print("Applies to by search:", count)

        # Leaving these out for now
        sets = ResourceTileTree.get_tiles(graph_slug="set")
        for regular_set in sets:
            if regular_set.aliased_data.members:
                # user=True is shorthand for "do not restrict by user"
                # does not allow for nested (unless bubbling up implemented)

                # TODO: as I understand it, similarly to AORM, I can do something like "member.id for member in regulur_set.members" but
                # I got a little confused about how to achieve that
                print(regular_set.aliased_data.members.aliased_data.members)
                members = [str(member2['resourceId']) for _, member in regular_set.aliased_data.members.data.items() if member for member2 in member]
                if not resourceinstanceid or str(resourceinstanceid) in members:
                    def _regular_set_query(members):
                        query = Query(se=_se)
                        bool_query = Bool()
                        print(members, 'members')
                        bool_query.must(Ids(ids=members))
                        query.add_query(bool_query)
                        return query
                    results = self._apply_set(_se, f"r:{regular_set.resourceinstanceid}", partial(_regular_set_query, members), resourceinstanceid=resourceinstanceid)
                    if self.wait:
                        self.wait_for_completion(_se, results)

    def wait_for_completion(self, _se, results):
        tasks_client = _se.make_tasks_client()
        while results:
            result = results[0]
            task_id = result["task"]
            status = tasks_client.get(task_id=task_id)
            if status["completed"]:
                results.remove(result)
            else:
                print(task_id, "not yet completed")
            time.sleep(0.1)
