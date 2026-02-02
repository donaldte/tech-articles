from __future__ import annotations

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import TimeSlotConfiguration, AvailabilityRule, ExceptionDate


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
                'class': 'form-input',
                'min': '15',
                'step': '15',
            }),
            'max_appointments_per_slot': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': '1',
            }),
            'timezone': forms.Select(attrs={
                'class': 'form-select',
            }),
            'minimum_booking_hours': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': '0',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox',
            }),
        }


class AvailabilityRuleForm(forms.ModelForm):
    """Form for creating/editing availability rules."""
    
    class Meta:
        model = AvailabilityRule
        fields = [
            'weekday',
            'start_time',
            'end_time',
            'is_recurring',
            'is_active',
        ]
        widgets = {
            'weekday': forms.Select(attrs={
                'class': 'form-select',
            }),
            'start_time': forms.TimeInput(attrs={
                'class': 'form-input',
                'type': 'time',
            }),
            'end_time': forms.TimeInput(attrs={
                'class': 'form-input',
                'type': 'time',
            }),
            'is_recurring': forms.CheckboxInput(attrs={
                'class': 'form-checkbox',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox',
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError(_("End time must be after start time"))
        
        return cleaned_data


class ExceptionDateForm(forms.ModelForm):
    """Form for adding exception dates (holidays, absences)."""
    
    class Meta:
        model = ExceptionDate
        fields = [
            'date',
            'reason',
            'is_active',
        ]
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date',
            }),
            'reason': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': _('Holiday, vacation, etc.'),
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox',
            }),
        }
