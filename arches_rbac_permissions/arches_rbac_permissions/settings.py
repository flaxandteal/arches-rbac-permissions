from arches_inclusion_rule.settings import *
from arches_saved_search.settings import *
from arches_user_datatype.settings import *
from arches_semantic_roles.settings import *

ARCHES_RBAC_PERMISSIONS_APPS += (
    "arches_semantic_roles",
)
