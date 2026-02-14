"""
Newsletter subscriber forms for dashboard CRUD operations.
"""
from django import forms
from django.utils.translation import gettext_lazy as _

from tech_articles.newsletter.models import NewsletterSubscriber


class NewsletterSubscriberForm(forms.ModelForm):
    """Form for creating and updating newsletter subscribers."""

    class Meta:
        model = NewsletterSubscriber
        fields = ["email", "language", "status", "tags", "is_active", "is_confirmed"]
        widgets = {
            "email": forms.EmailInput(attrs={
                "class": "dashboard-input",
                "placeholder": _("Enter subscriber email"),
                "autocomplete": "off",
            }),
            "language": forms.Select(attrs={
                "class": "dashboard-select",
            }),
            "status": forms.Select(attrs={
                "class": "dashboard-select",
            }),
            "tags": forms.TextInput(attrs={
                "class": "dashboard-input",
                "placeholder": _("Comma-separated tags (e.g., premium, developer, designer)"),
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "dashboard-checkbox",
            }),
            "is_confirmed": forms.CheckboxInput(attrs={
                "class": "dashboard-checkbox",
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip()
        if not email:
            raise forms.ValidationError(_("Email is required."))

        # Check for duplicates excluding current instance
        qs = NewsletterSubscriber.objects.filter(email__iexact=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(_("A subscriber with this email already exists."))

        return email
