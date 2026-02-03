"""
Availability rule forms for dashboard CRUD operations.
"""
from django import forms
from django.utils.translation import gettext_lazy as _

from tech_articles.appointments.models import AvailabilityRule


class AvailabilityRuleForm(forms.ModelForm):
    """Form for creating and updating availability rules."""

    class Meta:
        model = AvailabilityRule
        fields = ["weekday", "start_time", "end_time", "is_active"]
        widgets = {
            "weekday": forms.Select(attrs={
                "class": "dashboard-select",
            }),
            "start_time": forms.TimeInput(attrs={
                "class": "dashboard-input",
                "type": "time",
            }),
            "end_time": forms.TimeInput(attrs={
                "class": "dashboard-input",
                "type": "time",
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "dashboard-checkbox",
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError(_("End time must be after start time."))

        return cleaned_data
