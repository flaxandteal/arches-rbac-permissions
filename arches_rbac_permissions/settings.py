import os
import inspect
import semantic_version

MIDDLEWARE = []
ES_MAPPING_MODIFIER_CLASSES = []
DATATYPE_LOCATIONS = []

try:
    from arches.settings import *
except ImportError:
    pass

APP_NAME = "arches_rbac_permissions"
APP_VERSION = semantic_version.Version(major=0, minor=0, patch=1)
APP_ROOT = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

ES_MAPPING_MODIFIER_CLASSES += ["arches_rbac_permissions.es_mapping_modifier.SetsEsMappingModifier"]
DATATYPE_LOCATIONS += ["arches_rbac_permissions.datatypes"]
MIDDLEWARE += [
    "arches_rbac_permissions.utils.middleware.CurrentUserMiddleware"
]
