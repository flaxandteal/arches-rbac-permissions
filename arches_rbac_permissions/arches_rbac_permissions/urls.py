from django.urls import include, path

urlpatterns = []
urlpatterns.append(path('', include('arches_inclusion_rule.urls')))
urlpatterns.append(path('', include('arches_saved_search.urls')))
urlpatterns.append(path('', include('arches_user_datatype.urls')))
urlpatterns.append(path('', include('arches_semantic_roles.urls')))
