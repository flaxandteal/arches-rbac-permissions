from django.conf import settings
from django.urls import re_path

from .views.inclusion_rule_select import paged_inclusion_rule_list, inclusion_rule_get, copy_inclusion_rule_from_saved_search, go_to_inclusion_rule_inspect

uuid_regex = settings.UUID_REGEX

urlpatterns = [
    re_path(
        r"^inclusion_rule/go_to_inclusion_rule_inspect$",
        go_to_inclusion_rule_inspect,
        name="go_to_inclusion_rule_inspect",
    ),
    re_path(
        r"^inclusion_rule/get_inclusion_rule_names_all$",
        paged_inclusion_rule_list,
        name="get_inclusion_rule_names_all",
    ),
    re_path(
        r"^inclusion_rule/get_inclusion_rule_names_one$",
        inclusion_rule_get,
        name="get_inclusion_rule_names_one",
    ),
    re_path(
        r"^inclusion_rule/copy_inclusion_rule_from_saved_search$",
        copy_inclusion_rule_from_saved_search,
        name="copy_inclusion_rule_from_saved_search",
    )
]
