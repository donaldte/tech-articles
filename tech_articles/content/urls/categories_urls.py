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
    path("categories/", CategoryListView.as_view(), name="categories_list"),
    path("categories/create/", CategoryCreateView.as_view(), name="categories_create"),
    path("categories/<uuid:pk>/edit/", CategoryUpdateView.as_view(), name="categories_update"),
    path("categories/<uuid:pk>/delete/", CategoryDeleteView.as_view(), name="categories_delete"),
]
