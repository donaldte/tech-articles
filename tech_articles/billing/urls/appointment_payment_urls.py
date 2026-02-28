"""
Appointment payment URL patterns.
Endpoints for paid appointment checkout flows (Stripe + PayPal).
Kept separate from subscription and article-purchase flows.
"""
from django.urls import path

from tech_articles.billing.views import (
    AppointmentPaymentCreateView,
    AppointmentPaymentSummaryView,
    AppointmentPaymentSuccessView,
    AppointmentPaymentPayPalReturnView,
)

urlpatterns = [
    path(
        "appointments/create/",
        AppointmentPaymentCreateView.as_view(),
        name="appointment_payment_create",
    ),
    path(
        "appointments/summary/<uuid:transaction_id>/",
        AppointmentPaymentSummaryView.as_view(),
        name="appointment_payment_summary",
    ),
    path(
        "appointments/success/<uuid:transaction_id>/",
        AppointmentPaymentSuccessView.as_view(),
        name="appointment_payment_success",
    ),
    path(
        "appointments/paypal-return/<uuid:transaction_id>/",
        AppointmentPaymentPayPalReturnView.as_view(),
        name="appointment_payment_paypal_return",
    ),
]
