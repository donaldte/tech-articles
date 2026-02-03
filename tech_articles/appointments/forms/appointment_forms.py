"""
Appointment forms for dashboard CRUD operations.
"""
from django import forms
from django.utils.translation import gettext_lazy as _

from tech_articles.appointments.models import Appointment


class AppointmentForm(forms.ModelForm):
    """Form for creating and updating appointments."""

    class Meta:
        model = Appointment
        fields = ["user", "slot", "appointment_type", "status", "duration_minutes", "hourly_rate", 
                  "total_amount", "currency", "provider", "payment_status", "meeting_link", "notes"]
        widgets = {
            "user": forms.Select(attrs={
                "class": "dashboard-select",
            }),
            "slot": forms.Select(attrs={
                "class": "dashboard-select",
            }),
            "appointment_type": forms.Select(attrs={
                "class": "dashboard-select",
            }),
            "status": forms.Select(attrs={
                "class": "dashboard-select",
            }),
            "duration_minutes": forms.NumberInput(attrs={
                "class": "dashboard-input",
                "placeholder": "60",
            }),
            "hourly_rate": forms.NumberInput(attrs={
                "class": "dashboard-input",
                "placeholder": "0.00",
                "step": "0.01",
            }),
            "total_amount": forms.NumberInput(attrs={
                "class": "dashboard-input",
                "placeholder": "0.00",
                "step": "0.01",
            }),
            "currency": forms.TextInput(attrs={
                "class": "dashboard-input",
                "placeholder": "USD",
            }),
            "provider": forms.Select(attrs={
                "class": "dashboard-select",
            }),
            "payment_status": forms.Select(attrs={
                "class": "dashboard-select",
            }),
            "meeting_link": forms.URLInput(attrs={
                "class": "dashboard-input",
                "placeholder": _("Video conference or meeting URL"),
            }),
            "notes": forms.Textarea(attrs={
                "class": "dashboard-textarea",
                "placeholder": _("Additional notes or instructions"),
                "rows": 3,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["meeting_link"].required = False
        self.fields["notes"].required = False
