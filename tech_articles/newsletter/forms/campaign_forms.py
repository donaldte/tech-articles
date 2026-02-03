"""
Newsletter campaign forms for dashboard CRUD operations.
"""
from django import forms
from django.utils.translation import gettext_lazy as _

from tech_articles.newsletter.models import NewsletterCampaign


class NewsletterCampaignForm(forms.ModelForm):
    """Form for creating and updating newsletter campaigns."""

    class Meta:
        model = NewsletterCampaign
        fields = ["name", "schedule_mode", "is_active", "template_subject", "template_body"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "dashboard-input",
                "placeholder": _("Enter campaign name"),
                "autocomplete": "off",
            }),
            "schedule_mode": forms.Select(attrs={
                "class": "dashboard-select",
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "dashboard-checkbox",
            }),
            "template_subject": forms.TextInput(attrs={
                "class": "dashboard-input",
                "placeholder": _("Email subject template"),
                "autocomplete": "off",
            }),
            "template_body": forms.Textarea(attrs={
                "class": "dashboard-textarea",
                "placeholder": _("Email body template (HTML)"),
                "rows": 10,
            }),
        }

    def clean_name(self):
        name = self.cleaned_data.get("name", "").strip()
        if not name:
            raise forms.ValidationError(_("Campaign name is required."))
        return name
