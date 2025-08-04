from django.contrib.auth.models import User
from arches.app.search.elasticsearch_dsl_builder import Bool, Terms, Nested
from arches.app.utils.permission_backend import _get_permission_framework # would be nice to expose in ABI
from .utils.middleware import get_current_user

def get_sets_for_user(user: User, permission: str):
    return _get_permission_framework().get_sets_for_user(user, permission)

class SetsEsMappingModifier:
    """
    Add Sets to the Elasticsearch document
    """

    custom_search_path = "sets"

    def __init__(self):
        pass

    @staticmethod
    def get_mapping_property():
        """
        Identifies the document key where the custom ES document section is located.

        :return: ES document key
        :rtype String
        """
        return SetsEsMappingModifier.custom_search_path

    @staticmethod
    def add_search_terms(resourceinstance, document, terms):
        """
        Sets are essentially a membership caching tool, they do not get calculated during indexing 
        but when permissions are evaluated.
        Normally, this adds the custom ES search document section for the resource instance.
        :param resourceinstance: resource instance being indexed
        :param document: Original ES document for the Resource Instance
        :param terms: ES terms in the document
        """
        pass

    @staticmethod
    def add_search_filter(
        search_query, term, permitted_nodegroups, include_provisional
    ):
        """
        Adds modifies the term search_query to include the set filtering
        :param search_query: The original search term query
        :param term: The search term
        :param permitted_nodegroups: The nodegroups for which the user has access
        :param include_provisional: Whether to include provisional values
        """

        # TODO: previously, we set user=True to indicate machine-execution (e.g. commands)
        # but this should be reimplemented somehow here, reliably
        user = get_current_user()
        if user:
            sets = get_sets_for_user(user, "view_resourceinstance")
            if sets is not None: # Only None if no filtering should be done, but may be an empty set.
                subsearch_query = Bool()
                # Right now, Arches has its own permissions that we cannot hook (Coral patches it)
                # so we duplicate only the principal user check, as the User/Group one is probably not desirable
                # if doing set-driven.
                if sets:
                    subsearch_query.should(Nested(path="sets", query=Terms(field="sets.id", terms=list(sets))))
                if user and user.id:
                    subsearch_query.should(Nested(path="permissions", query=Terms(field="permissions.principal_user", terms=[int(user.id)])))
                search_query.must(subsearch_query)
        return search_query

    @staticmethod
    def get_mapping_definition():
        """
        Defines the ES structure of sets. Called when the initial ES resources index is created.

        :return: dict of the custom document section
        :rtype dict
        """
        return {
            "type": "nested",
            "properties": {"id": {"type": "keyword"}},
        }
