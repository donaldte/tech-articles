"""
Appointments views module.
"""
from .appointment_type_views import (
    AppointmentTypeListView,
    AppointmentTypeCreateView,
    AppointmentTypeUpdateView,
    AppointmentTypeDeleteView,
)
from .availability_views import (
    AvailabilitySettingsView,
    AvailabilityRuleListView,
    AvailabilityRuleCreateView,
    AvailabilityRuleUpdateView,
    AvailabilityRuleDeleteView,
)
from .appointment_views import (
    AppointmentListView,
    AppointmentCreateView,
    AppointmentUpdateView,
    AppointmentDetailView,
    AppointmentDeleteView,
)

__all__ = [
    "AppointmentTypeListView",
    "AppointmentTypeCreateView",
    "AppointmentTypeUpdateView",
    "AppointmentTypeDeleteView",
    "AvailabilitySettingsView",
    "AvailabilityRuleListView",
    "AvailabilityRuleCreateView",
    "AvailabilityRuleUpdateView",
    "AvailabilityRuleDeleteView",
    "AppointmentListView",
    "AppointmentCreateView",
    "AppointmentUpdateView",
    "AppointmentDetailView",
    "AppointmentDeleteView",
]
