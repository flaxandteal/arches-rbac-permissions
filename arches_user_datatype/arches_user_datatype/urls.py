from django.conf import settings
from django.urls import re_path

from .views.user_select import paged_user_list, user_get
from .views.django_group_select import paged_django_group_list, django_group_get
from .views.person_user import PersonUserSignupView
from .views.auth import PersonSignupView, PersonConfirmSignupView

uuid_regex = settings.UUID_REGEX

urlpatterns = [
    re_path(
        r"^group/get_group_names_all$",
        paged_django_group_list,
        name="get_group_names_all",
    ),
    re_path(
        r"^group/get_group_names_one$",
        django_group_get,
        name="get_group_names_one",
    ),
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
    )
]
