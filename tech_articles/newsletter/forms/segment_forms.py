"""
Subscriber segment forms for admin dashboard.
"""
from django import forms
from django.utils.translation import gettext_lazy as _

from tech_articles.newsletter.models import SubscriberSegment


class SubscriberSegmentForm(forms.ModelForm):
    """Form for creating and editing subscriber segments."""

    class Meta:
        model = SubscriberSegment
        fields = ["name", "description", "tags"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "dashboard-input",
                "placeholder": _("Enter segment name"),
                "autocomplete": "off",
            }),
            "description": forms.Textarea(attrs={
                "class": "dashboard-textarea",
                "placeholder": _("Optional description for this segment"),
                "rows": 3,
            }),
            "tags": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["description"].required = False
        self.fields["tags"].required = False

    def clean_name(self):
        name = self.cleaned_data.get("name", "").strip()
        if not name:
            raise forms.ValidationError(_("Segment name is required."))

        # Check for duplicates excluding current instance
        qs = SubscriberSegment.objects.filter(name__iexact=name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(_("A segment with this name already exists."))

        return name
