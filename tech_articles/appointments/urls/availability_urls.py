"""
Availability URL patterns for dashboard CRUD operations.
"""
from django.urls import path

from tech_articles.appointments.views import (
    AvailabilitySettingsView,
    AvailabilityRuleApiView,
    AppointmentSettingsAdminView,
)

urlpatterns = [
    path("availability/", AvailabilitySettingsView.as_view(), name="availability_settings"),
    path("availability/api/rules/", AvailabilityRuleApiView.as_view(), name="api_availability_rules"),
    path("settings/", AppointmentSettingsAdminView.as_view(), name="appointment_settings"),
]
