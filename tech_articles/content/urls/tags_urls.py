"""
Tag URL patterns for dashboard CRUD operations.
"""
from django.urls import path

from tech_articles.content.views import (
    TagListView,
    TagCreateView,
    TagUpdateView,
    TagDeleteView,
)

urlpatterns = [
    path("tags/", TagListView.as_view(), name="tags_list"),
    path("tags/create/", TagCreateView.as_view(), name="tags_create"),
    path("tags/<uuid:pk>/edit/", TagUpdateView.as_view(), name="tags_update"),
    path("tags/<uuid:pk>/delete/", TagDeleteView.as_view(), name="tags_delete"),
]
