from django.conf import settings
from django.urls import re_path

from .views.group_manager import GroupManagerView

uuid_regex = settings.UUID_REGEX

urlpatterns = [
    re_path(r'^groupmanager/(?P<grouping>[a-zA-Z_-]+)/?$',
        GroupManagerView.as_view(),
        name='groupmanager'
    ),
    re_path(r'^groupmanager/(?P<grouping>[a-zA-Z_-]+)/(?P<resourceid>%s|())$' % uuid_regex,
        GroupManagerView.as_view(),
        name='groupmanager_for_resource'
    )
]
