"""
Article URL patterns for dashboard CRUD operations.
"""
from django.urls import path

from tech_articles.content.views import (
    ArticleListView,
    ArticleCreateView,
    ArticleUpdateView,
    ArticleDetailView,
    ArticleDeleteView,
)

urlpatterns = [
    path("articles/", ArticleListView.as_view(), name="articles_list"),
    path("articles/create/", ArticleCreateView.as_view(), name="articles_create"),
    path("articles/<uuid:pk>/", ArticleDetailView.as_view(), name="articles_detail"),
    path("articles/<uuid:pk>/edit/", ArticleUpdateView.as_view(), name="articles_update"),
    path("articles/<uuid:pk>/delete/", ArticleDeleteView.as_view(), name="articles_delete"),
]
