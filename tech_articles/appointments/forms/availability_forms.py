"""
Availability rule forms for appointments.
"""
from __future__ import annotations

from django import forms
from django.utils.translation import gettext_lazy as _

from tech_articles.appointments.models import AvailabilityRule, ExceptionDate


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
                'class': 'dashboard-input',
            }),
            'start_time': forms.TimeInput(attrs={
                'class': 'dashboard-input',
                'type': 'time',
            }),
            'end_time': forms.TimeInput(attrs={
                'class': 'dashboard-input',
                'type': 'time',
            }),
            'is_recurring': forms.CheckboxInput(attrs={
                'class': 'dashboard-checkbox',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'dashboard-checkbox',
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
                'class': 'dashboard-input',
                'type': 'date',
            }),
            'reason': forms.TextInput(attrs={
                'class': 'dashboard-input',
                'placeholder': _('Holiday, vacation, etc.'),
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'dashboard-checkbox',
            }),
        }
