import os
import inspect
import semantic_version

DATATYPE_LOCATIONS = []
INSTALLED_APPS = ()
RULE_LOCATIONS = []

try:
    from arches.settings import *
except ImportError:
    pass

APP_NAME = "arches_inclusion_rule"
APP_VERSION = semantic_version.Version(major=0, minor=0, patch=1)
APP_ROOT = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

DATATYPE_LOCATIONS += ["arches_rbac_permissions.datatypes"]
RULE_LOCATIONS += ["arches_rbac_permissions.rules"]

INSTALLED_APPS = (
    *INSTALLED_APPS,
    "arches_querysets",
)
