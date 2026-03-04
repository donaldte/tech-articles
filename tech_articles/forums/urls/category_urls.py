"""
Forum category URL patterns for dashboard CRUD + public listing.
"""
from django.urls import path

from tech_articles.forums.views import (
    ForumCategoryPublicListView,
    ForumCategoryListView,
    ForumCategoryCreateView,
    ForumCategoryUpdateView,
    ForumCategoryDeleteView,
)

urlpatterns = [
    # Public
    path("", ForumCategoryPublicListView.as_view(), name="category_list"),

    # Dashboard (admin)
    path(
        "dashboard/categories/",
        ForumCategoryListView.as_view(),
        name="categories_list",
    ),
    path(
        "dashboard/categories/create/",
        ForumCategoryCreateView.as_view(),
        name="categories_create",
    ),
    path(
        "dashboard/categories/<uuid:pk>/edit/",
        ForumCategoryUpdateView.as_view(),
        name="categories_update",
    ),
    path(
        "dashboard/categories/<uuid:pk>/delete/",
        ForumCategoryDeleteView.as_view(),
        name="categories_delete",
    ),
]
