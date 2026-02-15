"""
Home appointment URL patterns for public-facing booking flow.
"""
from django.urls import path

from tech_articles.appointments.views import (
    AppointmentListHomeView,
    AppointmentDetailHomeView,
    AppointmentPaymentHomeView,
)

urlpatterns = [
    path("book/", AppointmentListHomeView.as_view(), name="appointments_book"),
    path("book/<int:slot_id>/detail/", AppointmentDetailHomeView.as_view(), name="appointments_book_detail"),
    path("book/<int:slot_id>/payment/", AppointmentPaymentHomeView.as_view(), name="appointments_book_payment"),
]
