"""
URL configuration for public-facing article views under content namespace.
These URLs handle article listing, detail pages, and all article-related APIs.
Included at root level in config/urls.py with content namespace.
"""
from django.urls import path

from tech_articles.content.views import (
    ArticlesListView,
    ArticleDetailView,
    ArticlePreviewView,
    ArticlesApiView,
    FeaturedArticlesApiView,
    RelatedArticlesApiView,
    CategoriesApiView,
    ArticleClapApiView,
    ArticleLikeApiView,
    ArticleCommentApiView,
    CommentLikeApiView,
)

# Note: These URLs are included in config/urls.py at root level with namespace="content"
# So they're accessible as content:articles_list, content:api_articles, etc.

urlpatterns = [
    # Article listing and detail pages
    path("articles/", ArticlesListView.as_view(), name="articles_list"),
    path("articles/<slug:slug>/", ArticleDetailView.as_view(), name="article_detail"),
    path("articles/preview/", ArticlePreviewView.as_view(), name="article_preview"),  # Deprecated
    
    # Article listing and data APIs
    path("api/articles/", ArticlesApiView.as_view(), name="api_articles"),
    path("api/articles/featured/", FeaturedArticlesApiView.as_view(), name="api_featured_articles"),
    path("api/articles/related/", RelatedArticlesApiView.as_view(), name="api_related_articles"),
    path("api/categories/", CategoriesApiView.as_view(), name="api_categories"),
    
    # Interactive APIs for articles
    path("api/articles/<uuid:article_id>/clap/", ArticleClapApiView.as_view(), name="api_article_clap"),
    path("api/articles/<uuid:article_id>/like/", ArticleLikeApiView.as_view(), name="api_article_like"),
    path("api/articles/<uuid:article_id>/comments/", ArticleCommentApiView.as_view(), name="api_article_comments"),
    
    # Comment interaction APIs
    path("api/comments/<uuid:comment_id>/like/", CommentLikeApiView.as_view(), name="api_comment_like"),
]
