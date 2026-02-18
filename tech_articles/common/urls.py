from django.urls import path

from .views import (
    ArticleClapApiView,
    ArticleCommentApiView,
    ArticleDetailView,
    ArticleLikeApiView,
    ArticlePreviewView,
    ArticlesApiView,
    ArticlesListView,
    AppointmentDetailHomeView,
    AppointmentListHomeView,
    AppointmentPaymentHomeView,
    CategoriesApiView,
    CommentLikeApiView,
    FeaturedArticlesApiView,
    HomePageView,
    RelatedArticlesApiView,
)

app_name = "common"

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("articles/", ArticlesListView.as_view(), name="articles_list"),
    path("articles/<slug:slug>/", ArticleDetailView.as_view(), name="article_detail"),
    path("articles/preview/", ArticlePreviewView.as_view(), name="article_preview"),  # Deprecated

    # API endpoints (JsonResponse)
    path("api/articles/", ArticlesApiView.as_view(), name="api_articles"),
    path("api/articles/featured/", FeaturedArticlesApiView.as_view(), name="api_featured_articles"),
    path("api/articles/related/", RelatedArticlesApiView.as_view(), name="api_related_articles"),
    path("api/categories/", CategoriesApiView.as_view(), name="api_categories"),
    
    # Interactive APIs
    path("api/articles/<uuid:article_id>/clap/", ArticleClapApiView.as_view(), name="api_article_clap"),
    path("api/articles/<uuid:article_id>/like/", ArticleLikeApiView.as_view(), name="api_article_like"),
    path("api/articles/<uuid:article_id>/comments/", ArticleCommentApiView.as_view(), name="api_article_comments"),
    path("api/comments/<uuid:comment_id>/like/", CommentLikeApiView.as_view(), name="api_comment_like"),

    path("appointments/book/", AppointmentListHomeView.as_view(), name="appointments_book"),
    path(
        "appointments/book/<str:slot_id>/detail/",
        AppointmentDetailHomeView.as_view(),
         name="appointments_book_detail"
    ),
    path(
        "appointments/book/<str:slot_id>/payment/",
        AppointmentPaymentHomeView.as_view(),
         name="appointments_book_payment"
    ),
]
