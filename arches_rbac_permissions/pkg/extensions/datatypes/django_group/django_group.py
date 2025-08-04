"""User data type for associating with models.

Datatype to extend possible node values to Django groups.
"""


from arches.app.models.models import Widget

text: Widget = Widget.objects.get(name="django-group")

details: dict[str, str | Widget | bool | None] = {
    "datatype": "django-group",
    "iconclass": "fa fa-location-arrow",
    "modulename": "arches_rbac_permissions.datatypes.django_group",
    "classname": "DjangoGroupDataType",
    "defaultwidget": text,
    "defaultconfig": None,
    "configcomponent": None,
    "configname": None,
    "isgeometric": False,
    "issearchable": False,
}
