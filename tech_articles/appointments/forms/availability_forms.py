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

        # Block rule if it overlaps with any existing Manual/One-off slots in DB
        from tech_articles.appointments.models import AppointmentSlot
        weekday_map = {'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3, 'fri': 4, 'sat': 5, 'sun': 6}
        weekday_val = cleaned_data.get("weekday")
        
        if weekday_val:
            target_weekday = weekday_map.get(weekday_val)

            # Check for any existing individual slots that overlap
            conflicting_slots = AppointmentSlot.objects.filter(
                start_at__time__lt=end_time,
                end_at__time__gt=start_time
            )
            
            for slot in conflicting_slots:
                # We check the weekday of the slot matches the rule's weekday
                if slot.start_at.weekday() == target_weekday:
                    raise forms.ValidationError(
                        _("This rule overlaps with a specific slot on %(date)s (%(start)s - %(end)s).") 
                        % {
                            'date': slot.start_at.date(), 
                            'start': slot.start_at.strftime('%H:%M'),
                            'end': slot.end_at.strftime('%H:%M')
                        }
                    )

        return cleaned_data
