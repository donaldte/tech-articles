"""
Appointment type forms for dashboard CRUD operations.
"""
from django import forms
from django.utils.translation import gettext_lazy as _

from tech_articles.appointments.models import AppointmentType


class AppointmentTypeForm(forms.ModelForm):
    """Form for creating and updating appointment types."""

    class Meta:
        model = AppointmentType
        fields = ["name", "description", "is_active", "base_hourly_rate", "currency", "allowed_durations_minutes", "pricing_rules_json"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "dashboard-input",
                "placeholder": _("Enter appointment type name"),
                "autocomplete": "off",
            }),
            "description": forms.Textarea(attrs={
                "class": "dashboard-textarea",
                "placeholder": _("Optional description for this appointment type"),
                "rows": 3,
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "dashboard-checkbox",
            }),
            "base_hourly_rate": forms.NumberInput(attrs={
                "class": "dashboard-input",
                "placeholder": "0.00",
                "step": "0.01",
            }),
            "currency": forms.TextInput(attrs={
                "class": "dashboard-input",
                "placeholder": "USD",
            }),
            "allowed_durations_minutes": forms.TextInput(attrs={
                "class": "dashboard-input",
                "placeholder": "30,60,90",
            }),
            "pricing_rules_json": forms.Textarea(attrs={
                "class": "dashboard-textarea",
                "placeholder": _("JSON rules for dynamic pricing"),
                "rows": 3,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["description"].required = False
        self.fields["pricing_rules_json"].required = False

    def clean_name(self):
        name = self.cleaned_data.get("name", "").strip()
        if not name:
            raise forms.ValidationError(_("Appointment type name is required."))

        # Check for duplicates excluding current instance
        qs = AppointmentType.objects.filter(name__iexact=name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(_("An appointment type with this name already exists."))

        return name
