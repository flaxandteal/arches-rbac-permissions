from django.conf import settings
from django.urls import re_path

from .views.user_select import paged_user_list, user_get
from .views.inclusion_rule_select import paged_inclusion_rule_list, inclusion_rule_get, copy_inclusion_rule_from_saved_search, go_to_inclusion_rule_inspect
from .views.person_user import PersonUserSignupView
from .views.auth import PersonSignupView, PersonConfirmSignupView
from .views.group_manager import GroupManagerView
from .views.saved_searches import SavedSearchesView

uuid_regex = settings.UUID_REGEX

urlpatterns = [
    re_path(
        r"^user/get_user_names_all$",
        paged_user_list,
        name="get_user_names_all",
    ),
    re_path(
        r"^user/get_user_names_one$",
        user_get,
        name="get_user_names_one",
    ),
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
    ),
    re_path(
        r"^person/signup-link$",
        PersonUserSignupView.as_view(),
        name="person_user_signup"
    ),
    re_path(
        r"^person-signup",
        PersonSignupView.as_view(),
        name="person_signup"
    ),
    re_path(
        r"^person-confirm-signup",
        PersonConfirmSignupView.as_view(),
        name="person_confirm_signup"
    ),
    re_path(r'^groupmanager/(?P<grouping>[a-zA-Z_-]+)/?$',
        GroupManagerView.as_view(),
        name='groupmanager'
    ),
    re_path(r'^groupmanager/(?P<grouping>[a-zA-Z_-]+)/(?P<resourceid>%s|())$' % uuid_regex,
        GroupManagerView.as_view(),
        name='groupmanager_for_resource'
    ),
    re_path(r'^savedsearches',
        SavedSearchesView.as_view(),
        name='savedsearches'
    ),
]
