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
    ArticleQuickCreateAPIView,
    ArticleDeleteAPIView,
    ArticleDashboardView,
    ArticleUpdateDetailsAPIView,
    ArticleUpdateSEOAPIView,
    ArticleUpdatePricingAPIView,
    # New mini-dashboard views
    ArticleManageDetailsView,
    ArticleManageSEOView,
    ArticleManagePricingView,
    ArticleManageContentView,
    ArticleCreateFullView,
    # ArticlePage API views
    ArticlePagesListAPIView,
    ArticlePageCreateAPIView,
    ArticlePageUpdateAPIView,
    ArticlePageDeleteAPIView,
    ArticlePageGetAPIView,
)

urlpatterns = [
    # List and Create
    path("articles/", ArticleListView.as_view(), name="articles_list"),
    path("articles/create/", ArticleCreateFullView.as_view(), name="articles_create"),

    # API endpoints
    path("articles/api/create/", ArticleQuickCreateAPIView.as_view(), name="articles_api_create"),
    path("articles/<uuid:pk>/api/delete/", ArticleDeleteAPIView.as_view(), name="articles_api_delete"),
    path("articles/<uuid:pk>/api/details/", ArticleUpdateDetailsAPIView.as_view(), name="articles_api_details"),
    path("articles/<uuid:pk>/api/seo/", ArticleUpdateSEOAPIView.as_view(), name="articles_api_seo"),
    path("articles/<uuid:pk>/api/pricing/", ArticleUpdatePricingAPIView.as_view(), name="articles_api_pricing"),

    # Article Pages API endpoints
    path("articles/<uuid:article_pk>/pages/", ArticlePagesListAPIView.as_view(), name="article_pages_list"),
    path("articles/<uuid:article_pk>/pages/create/", ArticlePageCreateAPIView.as_view(), name="article_page_create"),
    path("articles/<uuid:article_pk>/pages/<uuid:page_pk>/", ArticlePageGetAPIView.as_view(), name="article_page_get"),
    path("articles/<uuid:article_pk>/pages/<uuid:page_pk>/update/", ArticlePageUpdateAPIView.as_view(), name="article_page_update"),
    path("articles/<uuid:article_pk>/pages/<uuid:page_pk>/delete/", ArticlePageDeleteAPIView.as_view(), name="article_page_delete"),

    # Old dashboard (kept for backward compatibility)
    path("articles/<uuid:pk>/dashboard/", ArticleDashboardView.as_view(), name="articles_dashboard"),

    # New mini-dashboard routes
    path("articles/<uuid:pk>/manage/", ArticleManageDetailsView.as_view(), name="article_manage_details"),
    path("articles/<uuid:pk>/manage/seo/", ArticleManageSEOView.as_view(), name="article_manage_seo"),
    path("articles/<uuid:pk>/manage/pricing/", ArticleManagePricingView.as_view(), name="article_manage_pricing"),
    path("articles/<uuid:pk>/manage/content/", ArticleManageContentView.as_view(), name="article_manage_content"),

    # Other detail views
    path("articles/<uuid:pk>/", ArticleDetailView.as_view(), name="articles_detail"),
    path("articles/<uuid:pk>/edit/", ArticleUpdateView.as_view(), name="articles_update"),
    path("articles/<uuid:pk>/delete/", ArticleDeleteView.as_view(), name="articles_delete"),
]
