"""
Content views module.
Exports all views from feature-specific modules.
"""

from .article_public_views import (
    ArticlesListView,
    ArticleDetailView,
    ArticlesApiView,
    FeaturedArticlesApiView,
    RelatedArticlesApiView,
    CategoriesApiView,
    ArticleClapApiView,
    ArticleLikeApiView,
    ArticleCommentApiView,
    CommentLikeApiView,
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
from .categories_views import (
    CategoryListView,
    CategoryCreateView,
    CategoryUpdateView,
    CategoryDeleteView,
)
from .featured_articles_views import (
    FeaturedArticlesManageView,
)
from .publish_article_views import (
    PublishArticleAPIView,
)
from .tags_views import (
    TagListView,
    TagCreateView,
    TagUpdateView,
    TagDeleteView,
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
    # Featured Articles
    "FeaturedArticlesManageView",
    # Public-facing article views
    "ArticlesListView",
    "ArticleDetailView",
    # Article APIs
    "ArticlesApiView",
    "FeaturedArticlesApiView",
    "RelatedArticlesApiView",
    "CategoriesApiView",
    # Interactive APIs
    "ArticleClapApiView",
    "ArticleLikeApiView",
    "ArticleCommentApiView",
    "CommentLikeApiView",
]
