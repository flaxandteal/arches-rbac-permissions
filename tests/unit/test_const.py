"""Unit tests for the RBAC extension-type enums.

Both apps expose a ``RBACExtensionType`` whose ``RULES`` member must equal the
string ``"rules"`` — that value matches the ``RULE_LOCATIONS`` settings key the
apps register against, so a drift here would silently break rule discovery.
"""

from arches_inclusion_rule.const import RBACExtensionType as InclusionRuleType
from arches_semantic_roles.const import RBACExtensionType as SemanticRolesType


def test_inclusion_rule_rules_value():
    assert InclusionRuleType.RULES.value == "rules"


def test_semantic_roles_rules_value():
    assert SemanticRolesType.RULES.value == "rules"
