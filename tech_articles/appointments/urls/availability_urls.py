"""
Availability URL patterns for dashboard CRUD operations.
"""
from django.urls import path

from tech_articles.appointments.views import (
    AvailabilitySettingsView,
    AvailabilityRuleListView,
    AvailabilityRuleCreateView,
    AvailabilityRuleUpdateView,
    AvailabilityRuleDeleteView,
)

urlpatterns = [
    path("availability/", AvailabilitySettingsView.as_view(), name="availability_settings"),
    path("availability/rules/", AvailabilityRuleListView.as_view(), name="availability_rules_list"),
    path("availability/rules/create/", AvailabilityRuleCreateView.as_view(), name="availability_rules_create"),
    path("availability/rules/<uuid:pk>/edit/", AvailabilityRuleUpdateView.as_view(), name="availability_rules_update"),
    path("availability/rules/<uuid:pk>/delete/", AvailabilityRuleDeleteView.as_view(), name="availability_rules_delete"),
]
