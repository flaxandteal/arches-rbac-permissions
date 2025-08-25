import os
import inspect
import semantic_version

DATATYPE_LOCATIONS = []
ARCHES_RBAC_PERMISSIONS_APPS = ()
RULE_LOCATIONS = []

try:
    from arches.settings import *
except ImportError:
    pass

APP_NAME = "arches_inclusion_rule"
APP_VERSION = semantic_version.Version(major=0, minor=0, patch=1)
APP_ROOT = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

DATATYPE_LOCATIONS += ["arches_inclusion_rule.datatypes"]
RULE_LOCATIONS += ["arches_inclusion_rule.rules"]

SEARCH_BACKEND = "arches_inclusion_rule.utils.search.UpdatingSearchEngine"

ARCHES_RBAC_PERMISSIONS_APPS = (
    *ARCHES_RBAC_PERMISSIONS_APPS,
    "arches_saved_search",
    "arches_querysets",
)
