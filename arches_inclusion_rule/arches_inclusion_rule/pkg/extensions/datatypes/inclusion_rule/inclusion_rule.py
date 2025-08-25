"""Inclusion rule data type for associating with models.

Datatype to extend possible node values to Django users.
"""

from arches.app.models.models import Widget

text: Widget = Widget.objects.get(name="inclusion-rule")

details: dict[str, str | Widget | bool | None] = {
    "datatype": "inclusion-rule",
    "iconclass": "fa fa-location-arrow",
    "modulename": "arches_inclusion_rule.datatypes.inclusion_rule",
    "classname": "InclusionRuleDataType",
    "defaultwidget": text,
    "defaultconfig": None,
    "configcomponent": None,
    "configname": None,
    "isgeometric": False,
    "issearchable": False,
}
