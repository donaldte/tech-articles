"""
Category URL patterns for dashboard CRUD operations.
"""
from django.urls import path

from tech_articles.content.views import (
    CategoryListView,
    CategoryCreateView,
    CategoryUpdateView,
    CategoryDeleteView,
)

urlpatterns = [
    path("", CategoryListView.as_view(), name="categories_list"),
    path("create/", CategoryCreateView.as_view(), name="categories_create"),
    path("<uuid:pk>/edit/", CategoryUpdateView.as_view(), name="categories_update"),
    path("<uuid:pk>/delete/", CategoryDeleteView.as_view(), name="categories_delete"),
]
