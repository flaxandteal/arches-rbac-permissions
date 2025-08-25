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
INSTALLED_APPS = ()
AUTHENTICATION_BACKENDS = ()
WELL_KNOWN_RESOURCE_MODELS = []
RULE_LOCATIONS = []

try:
    from arches.settings import *
except ImportError:
    pass

APP_NAME = "arches_user_datatype"
APP_VERSION = semantic_version.Version(major=0, minor=0, patch=1)
APP_ROOT = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

DATATYPE_LOCATIONS += ["arches_user_datatype.datatypes"]

INSTALLED_APPS = (
    *INSTALLED_APPS,
    "arches_querysets",
)

SIGNUP_NODEGROUP = {
    "graph_slug": "person",
    "nodegroup_id": "b1f5c336-6a0e-11ee-b748-0242ac140009",
    "node_id": "b1f5c336-6a0e-11ee-b748-0242ac140009"
}

# For the user datatype to be useful, this is important to have in-built,
# but there are other use-cases too.
ENABLE_USER_SIGNUP = False
