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
    AvailabilityRuleApiView,
    AppointmentSettingsAdminView,
)
from .appointment_views import (
    AppointmentListView,
    AppointmentDetailView,
    UpdateMeetingLinkApiView,
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
    "AvailabilityRuleApiView",
    "AppointmentSettingsAdminView",
    "AppointmentListView",
    "AppointmentDetailView",
    "UpdateMeetingLinkApiView",
    "AppointmentSlotListView",
    "AppointmentSlotCreateView",
    "AppointmentSlotDeleteView",
]
