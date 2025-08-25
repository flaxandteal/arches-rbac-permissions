from django.conf import settings
from django.urls import re_path

from .views.saved_searches import SavedSearchesView

uuid_regex = settings.UUID_REGEX

urlpatterns = [
    re_path(r'^savedsearches',
        SavedSearchesView.as_view(),
        name='savedsearches'
    ),
]
