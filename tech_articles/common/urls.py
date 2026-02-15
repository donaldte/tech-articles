from django.urls import path

from .views import ArticleDetailView, ArticlePreviewView, ArticlesListView, HomePageView, AppointmentListHomeView, \
    AppointmentDetailHomeView, AppointmentPaymentHomeView

app_name = "common"

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("articles/", ArticlesListView.as_view(), name="articles_list"),
    path("articles/detail/", ArticleDetailView.as_view(), name="article_detail"),
    path("articles/preview/", ArticlePreviewView.as_view(), name="article_preview"),
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
