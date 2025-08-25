import os
from pathlib import Path
import inspect
import semantic_version

try:
    import tomllib
except ImportError:
    from pip._vendor import tomli as tomllib

MIDDLEWARE = []
DATATYPE_LOCATIONS = []
PERMISSION_LOCATIONS = []
ARCHES_RBAC_PERMISSIONS_APPS = ()
AUTHENTICATION_BACKENDS = ()
WELL_KNOWN_RESOURCE_MODELS = []
RULE_LOCATIONS = []

try:
    from arches.settings import *
except ImportError:
    pass

APP_NAME = "arches_saved_search"
APP_VERSION = semantic_version.Version(major=0, minor=0, patch=1)
APP_ROOT = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

DATATYPE_LOCATIONS += ["arches_saved_search.datatypes"]
ARCHES_RBAC_PERMISSIONS_APPS = (
    *ARCHES_RBAC_PERMISSIONS_APPS,
    "arches_querysets",
)
