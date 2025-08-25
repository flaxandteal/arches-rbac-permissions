"""Inclusion rule data type for associating with models.

Datatype to extend possible node values to Django inclusion rule.
"""


import logging

from arches.app.datatypes.base import BaseDataType
from arches.app.models.tile import Tile
from arches_rbac_permissions.models import InclusionRule


logger: logging.Logger = logging.getLogger(__name__)

class InclusionRuleDataType(BaseDataType):
    """DataType for an Inclusion Rule."""

    def append_to_document(self, document, nodevalue, nodeid, tile, provisional=False):
        ...

    def get_search_terms(self, nodevalue, nodeid=None):
        return []

    def get_display_value(self, tile, node, **kwargs):
        if (inclusion_rule := self.get_inclusion_rule(tile, str(node.nodeid))):
            return self._get_display_value_for_inclusion_rule(inclusion_rule)
        return ""

    def _get_display_value_for_inclusion_rule(self, inclusion_rule: InclusionRule) -> str:
        return inclusion_rule.name

    def get_inclusion_rule(self, tile: Tile, nodeid: str) -> InclusionRule:
        data = self.get_tile_data(tile)
        if data:
            raw_value = data.get(nodeid)
            if raw_value and (inclusion_rule_id := raw_value.get("inclusionRuleId")):
                inclusion_rule = InclusionRule.objects.get(pk=inclusion_rule_id)
                return inclusion_rule

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
                "inclusionRuleId": {
                    "type": "text"
                }
            }
        }
        return mapping
