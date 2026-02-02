"""
Time slot configuration forms for appointments.
"""
from __future__ import annotations

from django import forms
from django.utils.translation import gettext_lazy as _

from tech_articles.appointments.models import TimeSlotConfiguration


class TimeSlotConfigurationForm(forms.ModelForm):
    """Form for configuring time slot settings."""
    
    class Meta:
        model = TimeSlotConfiguration
        fields = [
            'slot_duration_minutes',
            'max_appointments_per_slot',
            'timezone',
            'minimum_booking_hours',
            'is_active',
        ]
        widgets = {
            'slot_duration_minutes': forms.NumberInput(attrs={
                'class': 'dashboard-input',
                'min': '15',
                'step': '15',
                'placeholder': _('60'),
            }),
            'max_appointments_per_slot': forms.NumberInput(attrs={
                'class': 'dashboard-input',
                'min': '1',
                'placeholder': _('1'),
            }),
            'timezone': forms.Select(attrs={
                'class': 'dashboard-input',
            }),
            'minimum_booking_hours': forms.NumberInput(attrs={
                'class': 'dashboard-input',
                'min': '0',
                'placeholder': _('24'),
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'dashboard-checkbox',
            }),
        }
