"""
Appointment type URL patterns for dashboard CRUD operations.
"""
from django.urls import path

from tech_articles.appointments.views import (
    AppointmentTypeListView,
    AppointmentTypeCreateView,
    AppointmentTypeUpdateView,
    AppointmentTypeDeleteView,
)

urlpatterns = [
    path("types/", AppointmentTypeListView.as_view(), name="appointment_types_list"),
    path("types/create/", AppointmentTypeCreateView.as_view(), name="appointment_types_create"),
    path("types/<uuid:pk>/edit/", AppointmentTypeUpdateView.as_view(), name="appointment_types_update"),
    path("types/<uuid:pk>/delete/", AppointmentTypeDeleteView.as_view(), name="appointment_types_delete"),
]
