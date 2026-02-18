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
    AppointmentSlotListView,
    AppointmentSlotCreateView,
    AppointmentSlotDeleteView,
)
from tech_articles.appointments.views.public_views import PublicAppointmentSlotsApiView

urlpatterns = [
    path("", AppointmentListView.as_view(), name="appointments_list"),
    path("create/", AppointmentCreateView.as_view(), name="appointments_create"),
    path("<uuid:pk>/", AppointmentDetailView.as_view(), name="appointments_detail"),
    path("<uuid:pk>/edit/", AppointmentUpdateView.as_view(), name="appointments_update"),
    path("<uuid:pk>/delete/", AppointmentDeleteView.as_view(), name="appointments_delete"),

    # Appointment Slots (Manual)
    path("slots/", AppointmentSlotListView.as_view(), name="appointment_slots_list"),
    path("slots/create/", AppointmentSlotCreateView.as_view(), name="appointment_slots_create"),
    path("slots/<uuid:pk>/delete/", AppointmentSlotDeleteView.as_view(), name="appointment_slots_delete"),

    path("api/slots/", PublicAppointmentSlotsApiView.as_view(), name="api_public_slots"),
]
