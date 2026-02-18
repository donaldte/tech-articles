from django import forms
from django.utils.translation import gettext_lazy as _
from tech_articles.appointments.models import AppointmentSlot, AvailabilityRule
from tech_articles.utils.enums import WeekdayChoices

class AppointmentSlotForm(forms.ModelForm):
    class Meta:
        model = AppointmentSlot
        fields = ["start_at", "end_at", "is_booked"]

    def clean(self):
        cleaned_data = super().clean()
        start_at = cleaned_data.get("start_at")
        end_at = cleaned_data.get("end_at")

        if start_at and end_at:
            if start_at >= end_at:
                raise forms.ValidationError(_("End time must be after start time."))

            # Block manual slot if it overlaps with a recurring AvailabilityRule
            weekday_map = {0: 'mon', 1: 'tue', 2: 'wed', 3: 'thu', 4: 'fri', 5: 'sat', 6: 'sun'}
            slot_weekday = weekday_map[start_at.weekday()]
            
            overlapping_rules = AvailabilityRule.objects.filter(
                weekday=slot_weekday,
                is_active=True,
                start_time__lt=end_at.time(),
                end_time__gt=start_at.time()
            )
            
            if overlapping_rules.exists():
                rule = overlapping_rules.first()
                raise forms.ValidationError(
                    _("Cannot create manual slot: Conflict with a recurring rule on %(day)s (%(start)s - %(end)s).") 
                    % {
                        'day': rule.get_weekday_display(),
                        'start': rule.start_time.strftime('%H:%M'),
                        'end': rule.end_time.strftime('%H:%M')
                    }
                )

        return cleaned_data
