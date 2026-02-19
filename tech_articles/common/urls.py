from django.urls import path

from .views import (
    ArticleDetailView,
    ArticlePreviewView,
    ArticlesApiView,
    ArticlesListView,
    AppointmentListHomeView,
    AppointmentDetailHomeView,
    AppointmentPaymentHomeView,
    AppointmentServiceSelectionView,
    CategoriesApiView,
    FeaturedArticlesApiView,
    HomePageView,
    RelatedArticlesApiView,
)

app_name = "common"

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("articles/", ArticlesListView.as_view(), name="articles_list"),
    path("articles/detail/", ArticleDetailView.as_view(), name="article_detail"),
    path("articles/preview/", ArticlePreviewView.as_view(), name="article_preview"),

    # API endpoints (JsonResponse)
    path("api/articles/", ArticlesApiView.as_view(), name="api_articles"),
    path("api/articles/featured/", FeaturedArticlesApiView.as_view(), name="api_featured_articles"),
    path("api/articles/related/", RelatedArticlesApiView.as_view(), name="api_related_articles"),
    path("api/categories/", CategoriesApiView.as_view(), name="api_categories"),

    path("appointments/book/", AppointmentListHomeView.as_view(), name="appointments_book"),
    path("appointments/book/select-service/", AppointmentServiceSelectionView.as_view(), name="appointments_book_service_selection"),
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
