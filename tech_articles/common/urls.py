from django.urls import path

from .views import (
    AppointmentDetailHomeView,
    AppointmentListHomeView,
    AppointmentPaymentHomeView,
    HomePageView,
)

# Import article URL patterns from content app
from tech_articles.content.urls.article_public_urls import urlpatterns as article_urls

app_name = "common"

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    
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

# Add article-related URLs (views from content app, but under common namespace)
urlpatterns += article_urls
