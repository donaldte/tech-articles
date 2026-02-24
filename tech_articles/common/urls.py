from django.urls import path

from .views import (
    AppointmentDetailHomeView,
    AppointmentListHomeView,
    AppointmentPaymentHomeView,
    AppointmentServiceSelectionView,
    HomePageView,
)

app_name = "common"

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    
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
