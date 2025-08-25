from enum import Enum

# TODO: This is not great, but curious if there's a better way in Django
class RBACExtensionType(Enum):
    RULES = "rules"
