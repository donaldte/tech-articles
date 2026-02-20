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
    PublishArticleAPIView,
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
    # Featured Articles
    FeaturedArticlesManageView,
)

urlpatterns = [
    # List and Create
    path("dasboard/articles/", ArticleListView.as_view(), name="articles_list"),
    path(
        "dasboard/articles/create/",
        ArticleCreateFullView.as_view(),
        name="articles_create",
    ),
    # API endpoints
    path(
        "dasboard/articles/<uuid:pk>/api/delete/",
        ArticleDeleteAPIView.as_view(),
        name="articles_api_delete",
    ),
    path(
        "dasboard/articles/<uuid:pk>/api/details/",
        ArticleUpdateDetailsAPIView.as_view(),
        name="articles_api_details",
    ),
    path(
        "dasboard/articles/<uuid:pk>/api/seo/",
        ArticleUpdateSEOAPIView.as_view(),
        name="articles_api_seo",
    ),
    path(
        "dasboard/articles/<uuid:pk>/api/pricing/",
        ArticleUpdatePricingAPIView.as_view(),
        name="articles_api_pricing",
    ),
    path(
        "dasboard/articles/<uuid:pk>/api/publish/",
        PublishArticleAPIView.as_view(),
        name="articles_api_publish",
    ),
    # Article Pages API endpoints
    path(
        "dasboard/articles/<uuid:article_pk>/pages/",
        ArticlePagesListAPIView.as_view(),
        name="article_pages_list",
    ),
    path(
        "dasboard/articles/<uuid:article_pk>/pages/api/create/",
        ArticlePageCreateAPIView.as_view(),
        name="article_page_create",
    ),
    path(
        "dasboard/articles/<uuid:article_pk>/pages/<uuid:page_pk>/",
        ArticlePageGetAPIView.as_view(),
        name="article_page_get",
    ),
    path(
        "dasboard/articles/<uuid:article_pk>/pages/<uuid:page_pk>/api/update/",
        ArticlePageUpdateAPIView.as_view(),
        name="article_page_update",
    ),
    path(
        "dasboard/articles/<uuid:article_pk>/pages/<uuid:page_pk>/api/delete/",
        ArticlePageDeleteAPIView.as_view(),
        name="article_page_delete",
    ),
    # Article Pages view-based routes (full page forms)
    path(
        "dasboard/articles/<uuid:article_pk>/pages/create/",
        ArticlePageCreateView.as_view(),
        name="article_page_create_view",
    ),
    path(
        "dasboard/articles/<uuid:article_pk>/pages/<uuid:page_pk>/edit/",
        ArticlePageUpdateView.as_view(),
        name="article_page_update_view",
    ),
    # New mini-dashboard routes
    path(
        "dasboard/articles/<uuid:pk>/manage/",
        ArticleManageDetailsView.as_view(),
        name="article_manage_details",
    ),
    path(
        "dasboard/articles/<uuid:pk>/manage/seo/",
        ArticleManageSEOView.as_view(),
        name="article_manage_seo",
    ),
    path(
        "dasboard/articles/<uuid:pk>/manage/pricing/",
        ArticleManagePricingView.as_view(),
        name="article_manage_pricing",
    ),
    path(
        "dasboard/articles/<uuid:pk>/manage/preview/",
        ArticleManagePreviewView.as_view(),
        name="article_manage_preview",
    ),
    path(
        "dasboard/articles/<uuid:pk>/manage/content/",
        ArticleManageContentView.as_view(),
        name="article_manage_content",
    ),
    # Featured Articles Management
    path(
        "dasboard/featured-articles/",
        FeaturedArticlesManageView.as_view(),
        name="featured_articles_manage",
    ),
]
