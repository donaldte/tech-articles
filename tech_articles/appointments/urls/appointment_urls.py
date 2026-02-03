"""
Appointment URL patterns for dashboard CRUD operations.
"""
from django.urls import path

from tech_articles.appointments.views import (
    AppointmentListView,
    AppointmentCreateView,
    AppointmentUpdateView,
    AppointmentDetailView,
    AppointmentDeleteView,
)

urlpatterns = [
    path("", AppointmentListView.as_view(), name="appointments_list"),
    path("create/", AppointmentCreateView.as_view(), name="appointments_create"),
    path("<uuid:pk>/", AppointmentDetailView.as_view(), name="appointments_detail"),
    path("<uuid:pk>/edit/", AppointmentUpdateView.as_view(), name="appointments_update"),
    path("<uuid:pk>/delete/", AppointmentDeleteView.as_view(), name="appointments_delete"),
]
