from django.urls import re_path

from .views.user_select import paged_user_list, user_get

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
    )
]
