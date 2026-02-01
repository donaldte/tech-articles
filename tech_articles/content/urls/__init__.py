"""
Content URLs module.
Main URL configuration for content management (categories, tags, articles).
Accessible at /content/ (after i18n prefix)
"""
from django.urls import path, include

from tech_articles.content.views import (
    CategoryListView,
    CategoryCreateView,
    CategoryUpdateView,
    CategoryDeleteView,
    TagListView,
    TagCreateView,
    TagUpdateView,
    TagDeleteView,
)

app_name = "content"

urlpatterns = [
    # =====================
    # CATEGORIES CRUD
    # =====================
    path("categories/", CategoryListView.as_view(), name="categories_list"),
    path("categories/create/", CategoryCreateView.as_view(), name="categories_create"),
    path("categories/<uuid:pk>/edit/", CategoryUpdateView.as_view(), name="categories_update"),
    path("categories/<uuid:pk>/delete/", CategoryDeleteView.as_view(), name="categories_delete"),

    # =====================
    # TAGS CRUD
    # =====================
    path("tags/", TagListView.as_view(), name="tags_list"),
    path("tags/create/", TagCreateView.as_view(), name="tags_create"),
    path("tags/<uuid:pk>/edit/", TagUpdateView.as_view(), name="tags_update"),
    path("tags/<uuid:pk>/delete/", TagDeleteView.as_view(), name="tags_delete"),
]
