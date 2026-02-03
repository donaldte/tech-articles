"""
Appointments forms module.
"""
from .appointment_type_forms import AppointmentTypeForm
from .availability_forms import AvailabilityRuleForm
from .appointment_forms import AppointmentForm

__all__ = [
    "AppointmentTypeForm",
    "AvailabilityRuleForm",
    "AppointmentForm",
]
