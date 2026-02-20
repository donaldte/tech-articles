"""
Dashboard URL configuration for Runbookly.
Organizes URLs for admin and user dashboard features.
"""

from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    # =====================
    # MAIN DASHBOARD
    # =====================
    path("", views.DashboardPageView.as_view(), name="home"),
    # =====================
    # MY SUBSCRIPTION (All Users)
    # =====================
    path(
        "my-subscription/", views.MySubscriptionView.as_view(), name="my_subscription"
    ),
    path(
        "my-subscription/invoices/", views.MyInvoicesView.as_view(), name="my_invoices"
    ),
    # =====================
    # MY APPOINTMENTS (All Users)
    # =====================
    path(
        "my-appointments/", views.MyAppointmentsView.as_view(), name="my_appointments"
    ),
    path(
        "my-appointments/book/",
        views.BookAppointmentView.as_view(),
        name="book_appointment",
    ),
    # =====================
    # SUPPORT & HELP
    # =====================
    path("support/", views.SupportView.as_view(), name="support"),
]
