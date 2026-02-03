"""
Resource URL patterns for dashboard CRUD operations.
"""
from django.urls import path

from tech_articles.resources.views import (
    ResourceListView,
    ResourceCreateView,
    ResourceUpdateView,
    ResourceDeleteView,
)

urlpatterns = [
    path("", ResourceListView.as_view(), name="resources_list"),
    path("create/", ResourceCreateView.as_view(), name="resources_create"),
    path("<uuid:pk>/edit/", ResourceUpdateView.as_view(), name="resources_update"),
    path("<uuid:pk>/delete/", ResourceDeleteView.as_view(), name="resources_delete"),
]
