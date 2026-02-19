"""
URL configuration for public-facing article views.
These URLs are mounted under the content app namespace.
"""
from django.urls import path

from tech_articles.content.views import (
    ArticleDetailView,
    ArticlePreviewView,
    ArticleClapApiView,
    ArticleLikeApiView,
    ArticleCommentApiView,
    CommentLikeApiView,
)

app_name = "content"

urlpatterns = [
    # Article detail with pagination support
    # Example: /articles/my-article-slug/?page=2
    path("articles/<slug:slug>/", ArticleDetailView.as_view(), name="article_detail"),
    
    # Deprecated preview view (redirects to ArticleDetailView)
    path("articles/preview/", ArticlePreviewView.as_view(), name="article_preview"),
    
    # Interactive APIs for articles
    path("api/articles/<uuid:article_id>/clap/", ArticleClapApiView.as_view(), name="api_article_clap"),
    path("api/articles/<uuid:article_id>/like/", ArticleLikeApiView.as_view(), name="api_article_like"),
    path("api/articles/<uuid:article_id>/comments/", ArticleCommentApiView.as_view(), name="api_article_comments"),
    
    # Comment interaction APIs
    path("api/comments/<uuid:comment_id>/like/", CommentLikeApiView.as_view(), name="api_comment_like"),
]
