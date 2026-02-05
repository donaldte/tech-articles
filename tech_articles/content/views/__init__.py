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
    # Article status API views
    ArticlePublishAPIView,
    ArticleArchiveAPIView,
    ArticleRestoreAPIView,
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
    # ArticlePage view-based views
    ArticlePageCreateView,
    ArticlePageUpdateView,
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
    # Article status API views
    "ArticlePublishAPIView",
    "ArticleArchiveAPIView",
    "ArticleRestoreAPIView",
    # New mini-dashboard views
    "ArticleManageDetailsView",
    "ArticleManageSEOView",
    "ArticleManagePricingView",
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
]
