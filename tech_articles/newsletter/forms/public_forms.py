"""
Public newsletter forms for user-facing subscription management.
"""
from django import forms
from django.utils.translation import gettext_lazy as _

from tech_articles.newsletter.models import NewsletterSubscriber
from tech_articles.utils.enums import LanguageChoices


class NewsletterSubscribeForm(forms.ModelForm):
    """Form for newsletter subscription (user-facing)."""

    email = forms.EmailField(
        label=_("Email address"),
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": _("Enter your email address"),
            "autocomplete": "email",
        }),
    )
    language = forms.ChoiceField(
        label=_("Preferred language"),
        choices=LanguageChoices.choices,
        initial=LanguageChoices.FR,
        widget=forms.Select(attrs={
            "class": "form-control",
        }),
    )
    consent = forms.BooleanField(
        label=_("I agree to receive newsletters and understand my data will be processed according to the privacy policy"),
        required=True,
        widget=forms.CheckboxInput(attrs={
            "class": "form-check-input",
        }),
    )

    class Meta:
        model = NewsletterSubscriber
        fields = ["email", "language"]

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        if NewsletterSubscriber.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(_("This email is already subscribed to our newsletter."))
        return email


class NewsletterUnsubscribeForm(forms.Form):
    """Form for newsletter unsubscription confirmation."""

    confirm = forms.BooleanField(
        label=_("I confirm that I want to unsubscribe from the newsletter"),
        required=True,
        widget=forms.CheckboxInput(attrs={
            "class": "form-check-input",
        }),
    )
