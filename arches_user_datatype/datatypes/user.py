"""User data type for associating with models.

Datatype to extend possible node values to Django users.
"""


import logging

from arches.app.datatypes.base import BaseDataType
from arches.app.models.models import Widget, Node
from arches.app.models.tile import Tile
from arches.app.search.search_term import SearchTerm
from django.contrib.auth.models import User


logger: logging.Logger = logging.getLogger(__name__)

class UserDataType(BaseDataType):
    """DataType for a Django User."""

    def append_to_document(self, document, nodevalue, nodeid, tile, provisional=False):
        if (user := self.get_user(tile, nodeid)):
            document["strings"].append(
                {"string": self._get_display_value_for_user(user), "nodegroup_id": tile.nodegroup_id}
            )

    def get_search_terms(self, nodevalue, nodeid=None):
        terms = []
        if nodevalue and "userId" in nodevalue:
            user = User.objects.get(pk=int(nodevalue["userId"]))
            # TODO: scrub on removal of a user
            terms.append(SearchTerm(value=self._get_display_value_for_user(user)))
        return terms

    def get_display_value(self, tile, node, **kwargs):
        if (user := self.get_user(tile, str(node.nodeid))):
            return self._get_display_value_for_user(user)
        return None

    def _get_display_value_for_user(self, user: User) -> str:
        return user.email or user.username

    def get_user(self, tile: Tile, nodeid: str) -> User:
        data = self.get_tile_data(tile)
        if data:
            raw_value = data.get(nodeid)
            if raw_value and (user_id := raw_value.get("userId")):
                user = User.objects.get(pk=user_id)
                return user

    def compile_json(self, tile, node, **kwargs):
        json = super().compile_json(tile, node, **kwargs)
        json.setdefault("@display_value", "")
        data = self.get_tile_data(tile)
        if data:
            json = data.get(str(node.nodeid), {})
            json["@display_value"] = self.get_display_value(tile, node)
        return json

    def default_es_mapping(self):
        mapping = {
            "properties": {
                "userId": {
                    "type": "integer"
                }
            }
        }
        return mapping
