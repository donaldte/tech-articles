"""
Content views module.
Exports all views from feature-specific modules.
"""
from .categories_views import (
    CategoryListView,
    CategoryCreateView,
    CategoryUpdateView,
    CategoryDeleteView,
)
from .tags_views import (
    TagListView,
    TagCreateView,
    TagUpdateView,
    TagDeleteView,
)
from .article_views import (
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
from .publish_article_views import (
    PublishArticleAPIView,
)

__all__ = [
    # Categories
    "CategoryListView",
    "CategoryCreateView",
    "CategoryUpdateView",
    "CategoryDeleteView",
    # Tags
    "TagListView",
    "TagCreateView",
    "TagUpdateView",
    "TagDeleteView",
    # Articles
    "ArticleListView",
    "ArticleDeleteAPIView",
    "ArticleUpdateDetailsAPIView",
    "ArticleUpdateSEOAPIView",
    "ArticleUpdatePricingAPIView",
    # New mini-dashboard views
    "ArticleManageDetailsView",
    "ArticleManageSEOView",
    "ArticleManagePricingView",
    "ArticleManagePreviewView",
    "ArticleManageContentView",
    "ArticleCreateFullView",
    # ArticlePage API views
    "ArticlePagesListAPIView",
    "ArticlePageCreateAPIView",
    "ArticlePageUpdateAPIView",
    "ArticlePageDeleteAPIView",
    "ArticlePageGetAPIView",
    # ArticlePage view-based views
    "ArticlePageCreateView",
    "ArticlePageUpdateView",
    # Publish API
    "PublishArticleAPIView",
]
