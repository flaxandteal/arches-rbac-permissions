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

try:
    from arches.settings import *
except ImportError:
    pass

APP_NAME = "arches_rbac_permissions"
APP_VERSION = semantic_version.Version(major=0, minor=0, patch=1)
APP_ROOT = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

GROUPINGS = {
    "groups": {
        "allowed_relationships": {
            "http://www.cidoc-crm.org/cidoc-crm/P107_has_current_or_former_member": (True, True),
        },
        "root_group": "d2368123-9628-49a2-b3dd-78ac6ee3e911",
        "graph_id": "07883c9e-b25c-11e9-975a-a4d18cec433a"
    },
    "permissions": {
        "allowed_relationships": {
            "http://www.cidoc-crm.org/cidoc-crm/P107_has_current_or_former_member": (True, False),
            "http://www.cidoc-crm.org/cidoc-crm/P104i_applies_to": (True, True),
            "http://www.cidoc-crm.org/cidoc-crm/P10i_contains": (True, True),
        },
        "root_group": "74e496c7-ec7e-43b8-a7b3-05bacf496794",
    }
}

DATATYPE_LOCATIONS += ["arches_rbac_permissions.datatypes"]
PERMISSION_LOCATIONS += ["arches_rbac_permissions.permissions"]
MIDDLEWARE += [
    "arches_rbac_permissions.utils.middleware.CurrentUserMiddleware"
]

USE_CASBIN = True
CASBIN_MODEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'permissions', 'casbin.conf')
CASBIN_RELOAD_QUEUE = os.getenv("CASBIN_RELOAD_QUEUE", "reloadQueue")

# TODO: this was previously read from OS as CASBIN_LISTEN
ENABLE_CASBIN_TRIGGER = False
CASBIN_TRIGGER_DEBOUNCE_SECONDS = 5.

AUTHENTICATION_BACKENDS = (
    *AUTHENTICATION_BACKENDS,
    "dauthz.backends.CasbinBackend",
)
PERMISSION_FRAMEWORK = "casbin.CasbinPermissionFramework"
INSTALLED_APPS = (
    *INSTALLED_APPS,
    "arches_querysets",
    "casbin_adapter.apps.CasbinAdapterConfig"
)

DAUTHZ = {
    # DEFAULT Dauthz enforcer
    "DEFAULT": {
        # Casbin model setting.
        "MODEL": {
            # Available Settings: "file", "text"
            "CONFIG_TYPE": "file",
            "CONFIG_FILE_PATH": CASBIN_MODEL,
            "CONFIG_TEXT": "",
        },
        # Casbin adapter .
        "ADAPTER": {
            "NAME": "casbin_adapter.adapter.Adapter",
            # 'OPTION_1': '',
        },
        "LOG": {
            # Changes whether Dauthz will log messages to the Logger.
            "ENABLED": False,
        },
    },
}

try:
    with (Path(__file__).parent / "wkrm.toml").open("rb") as wkrm_f:
        WELL_KNOWN_RESOURCE_MODELS += [model for _, model in tomllib.load(wkrm_f).items()]
except:
    with (Path(__file__).parent / "wkrm.toml").open("r") as wkrm_f:
        WELL_KNOWN_RESOURCE_MODELS += [model for _, model in tomllib.load(wkrm_f).items()]
