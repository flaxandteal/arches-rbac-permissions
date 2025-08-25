"""DjangoGroup data type for associating with models.

Datatype to extend possible node values to Django groups.
"""


import logging

from arches.app.datatypes.base import BaseDataType
from arches.app.models.models import Widget, Node
from arches.app.models.tile import Tile
from arches.app.search.search_term import SearchTerm
from django.contrib.auth.models import Group as DjangoGroup


logger: logging.Logger = logging.getLogger(__name__)

class DjangoGroupDataType(BaseDataType):
    """DataType for a Django Group."""

    def append_to_document(self, document, nodevalue, nodeid, tile, provisional=False):
        if (group := self.get_group(tile, nodeid)):
            document["strings"].append(
                {"string": self._get_display_value_for_group(group), "nodegroup_id": tile.nodegroup_id}
            )

    def get_search_terms(self, nodevalue, nodeid=None):
        terms = []
        if nodevalue and "groupId" in nodevalue:
            group = DjangoGroup.objects.get(pk=int(nodevalue["groupId"]))
            # TODO: scrub on removal of a group
            terms.append(SearchTerm(value=self._get_display_value_for_group(group)))
        return terms

    def get_display_value(self, tile, node, **kwargs):
        if (group := self.get_group(tile, str(node.nodeid))):
            return self._get_display_value_for_group(group)
        return None

    def _get_display_value_for_group(self, group: DjangoGroup) -> str:
        return group.name

    def get_group(self, tile: Tile, nodeid: str) -> DjangoGroup:
        data = self.get_tile_data(tile)
        if data:
            raw_value = data.get(nodeid)
            if raw_value and (group_id := raw_value.get("groupId")):
                group = DjangoGroup.objects.get(pk=group_id)
                return group

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
                "groupId": {
                    "type": "integer"
                }
            }
        }
        return mapping
