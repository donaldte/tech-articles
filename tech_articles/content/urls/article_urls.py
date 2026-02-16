"""
Article URL patterns for dashboard CRUD operations.
"""
from django.urls import path

from tech_articles.content.views import (
    ArticleListView,
    ArticleDeleteAPIView,
    ArticleUpdateDetailsAPIView,
    ArticleUpdateSEOAPIView,
    ArticleUpdatePricingAPIView,
    # New mini-dashboard views
    ArticleManageDetailsView,
    ArticleManageSEOView,
    ArticleManagePricingView,
    ArticleManagePreviewView,
    ArticleManageContentView,
    ArticleCreateFullView,
    # ArticlePage API views
    ArticlePagesListAPIView,
    ArticlePageCreateAPIView,
    ArticlePageUpdateAPIView,
    ArticlePageDeleteAPIView,
    ArticlePageGetAPIView,
    # ArticlePage view-based views
    ArticlePageCreateView,
    ArticlePageUpdateView,
)

urlpatterns = [
    # List and Create
    path("articles/", ArticleListView.as_view(), name="articles_list"),
    path("articles/create/", ArticleCreateFullView.as_view(), name="articles_create"),

    # API endpoints
    path("articles/<uuid:pk>/api/delete/", ArticleDeleteAPIView.as_view(), name="articles_api_delete"),
    path("articles/<uuid:pk>/api/details/", ArticleUpdateDetailsAPIView.as_view(), name="articles_api_details"),
    path("articles/<uuid:pk>/api/seo/", ArticleUpdateSEOAPIView.as_view(), name="articles_api_seo"),
    path("articles/<uuid:pk>/api/pricing/", ArticleUpdatePricingAPIView.as_view(), name="articles_api_pricing"),

    # Article Pages API endpoints
    path("articles/<uuid:article_pk>/pages/", ArticlePagesListAPIView.as_view(), name="article_pages_list"),
    path("articles/<uuid:article_pk>/pages/api/create/", ArticlePageCreateAPIView.as_view(), name="article_page_create"),
    path("articles/<uuid:article_pk>/pages/<uuid:page_pk>/", ArticlePageGetAPIView.as_view(), name="article_page_get"),
    path("articles/<uuid:article_pk>/pages/<uuid:page_pk>/api/update/", ArticlePageUpdateAPIView.as_view(), name="article_page_update"),
    path("articles/<uuid:article_pk>/pages/<uuid:page_pk>/api/delete/", ArticlePageDeleteAPIView.as_view(), name="article_page_delete"),

    # Article Pages view-based routes (full page forms)
    path("articles/<uuid:article_pk>/pages/create/", ArticlePageCreateView.as_view(), name="article_page_create_view"),
    path("articles/<uuid:article_pk>/pages/<uuid:page_pk>/edit/", ArticlePageUpdateView.as_view(), name="article_page_update_view"),

    # New mini-dashboard routes
    path("articles/<uuid:pk>/manage/", ArticleManageDetailsView.as_view(), name="article_manage_details"),
    path("articles/<uuid:pk>/manage/seo/", ArticleManageSEOView.as_view(), name="article_manage_seo"),
    path("articles/<uuid:pk>/manage/pricing/", ArticleManagePricingView.as_view(), name="article_manage_pricing"),
    path("articles/<uuid:pk>/manage/preview/", ArticleManagePreviewView.as_view(), name="article_manage_preview"),
    path("articles/<uuid:pk>/manage/content/", ArticleManageContentView.as_view(), name="article_manage_content"),
]
