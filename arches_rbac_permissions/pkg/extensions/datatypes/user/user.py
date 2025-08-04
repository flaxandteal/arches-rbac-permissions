"""User data type for associating with models.

Datatype to extend possible node values to Django users.
"""

from arches.app.models.models import Widget

text: Widget = Widget.objects.get(name="user")

details: dict[str, str | Widget | bool | None] = {
    "datatype": "user",
    "iconclass": "fa fa-location-arrow",
    "modulename": "arches_rbac_permissions.datatypes.user",
    "classname": "UserDataType",
    "defaultwidget": text,
    "defaultconfig": None,
    "configcomponent": None,
    "configname": None,
    "isgeometric": False,
    "issearchable": False,
}
