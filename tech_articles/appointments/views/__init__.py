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
    AvailabilityRuleApiView,
)
from .appointment_views import (
    AppointmentListView,
    AppointmentCreateView,
    AppointmentUpdateView,
    AppointmentDetailView,
    AppointmentDeleteView,
)
from .slot_views import (
    AppointmentSlotListView,
    AppointmentSlotCreateView,
    AppointmentSlotDeleteView,
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
    "AvailabilityRuleApiView",
    "AppointmentListView",
    "AppointmentCreateView",
    "AppointmentUpdateView",
    "AppointmentDetailView",
    "AppointmentDeleteView",
    "AppointmentSlotListView",
    "AppointmentSlotCreateView",
    "AppointmentSlotDeleteView",
]
