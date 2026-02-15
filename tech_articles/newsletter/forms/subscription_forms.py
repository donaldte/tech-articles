"""
Newsletter subscription form for public users.
"""
from django import forms
from django.utils.translation import gettext_lazy as _

from tech_articles.newsletter.models import NewsletterSubscriber


class NewsletterSubscriptionForm(forms.ModelForm):
    """Form for public newsletter subscription."""

    class Meta:
        model = NewsletterSubscriber
        fields = ["email", "language"]
        widgets = {
            "email": forms.EmailInput(attrs={
                "class": "form-input flex-1",
                "placeholder": _("Enter email"),
                "required": True,
                "aria-label": _("Email address"),
            }),
            "language": forms.Select(attrs={
                "class": "form-input",
                "required": True,
                "aria-label": _("Language"),
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        if not email:
            raise forms.ValidationError(_("Email is required."))

        # NOTE: duplicate email handling moved to view to support reactivation flow
        return email
