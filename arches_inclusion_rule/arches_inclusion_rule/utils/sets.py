from django.utils.translation import gettext as _
from arches.app.search.elasticsearch_dsl_builder import Bool, Terms, Query
from arches.app.search.mappings import RESOURCES_INDEX
from arches.app.search.search_engine_factory import SearchEngineInstance as se

class UnindexedError(Exception):
    def __init__(self, message, code=None):
        self.title = _("Unindexed Error")
        self.message = message
        self.code = code

    def __str__(self):
        return repr(self.message)

def get_sets_for_resource(resource):
    if not resource.resourceinstanceid:
        return []
    doc = get_index(resource)
    if (sets := doc.get("_source", {}).get("sets", [])):
        return sets
    return []

def get_index(resource, resourceinstanceid=None):
    """
    Gets the indexed document for a resource

    Keyword Arguments:
    resourceinstanceid -- the resource instance id to delete from related indexes, if supplied will use this over self.resourceinstanceid
    """

    if resourceinstanceid is None:
        resourceinstanceid = resource.resourceinstanceid
    resourceinstanceid = str(resourceinstanceid)

    # delete any related terms
    query = Query(se)
    bool_query = Bool()
    bool_query.must(Terms(field="_id", terms=[resourceinstanceid]))
    query.add_query(bool_query)
    query.include("sets")
    query.include("permissions.principal_user")
    results = query.search(index=RESOURCES_INDEX)
    if len(results["hits"]["hits"]) < 1:
        raise UnindexedError("This resource is not (yet) indexed")
    if len(results["hits"]["hits"]) > 1:
        raise RuntimeError("Resource instance ID exists multiple times in search index")
    return results["hits"]["hits"][0]

