"""
Newsletter forms for subscription management.
"""
import csv
import io
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from tech_articles.newsletter.models import (
    NewsletterSubscriber,
    SubscriberTag,
    SubscriberSegment,
)
from tech_articles.utils.enums import LanguageChoices, SubscriberStatus


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


class SubscriberFilterForm(forms.Form):
    """Form for filtering subscribers in admin dashboard."""

    status = forms.ChoiceField(
        label=_("Status"),
        choices=[("", _("All"))] + list(SubscriberStatus.choices),
        required=False,
        widget=forms.Select(attrs={
            "class": "dashboard-input",
        }),
    )
    language = forms.ChoiceField(
        label=_("Language"),
        choices=[("", _("All"))] + list(LanguageChoices.choices),
        required=False,
        widget=forms.Select(attrs={
            "class": "dashboard-input",
        }),
    )
    is_confirmed = forms.ChoiceField(
        label=_("Confirmed"),
        choices=[
            ("", _("All")),
            ("yes", _("Confirmed")),
            ("no", _("Not confirmed")),
        ],
        required=False,
        widget=forms.Select(attrs={
            "class": "dashboard-input",
        }),
    )
    search = forms.CharField(
        label=_("Search"),
        required=False,
        widget=forms.TextInput(attrs={
            "class": "dashboard-input",
            "placeholder": _("Search by email..."),
        }),
    )


class SubscriberImportForm(forms.Form):
    """Form for importing subscribers from CSV."""

    csv_file = forms.FileField(
        label=_("CSV file"),
        help_text=_("Upload a CSV file with columns: email, language"),
        widget=forms.FileInput(attrs={
            "class": "dashboard-input",
            "accept": ".csv",
        }),
    )

    def clean_csv_file(self):
        csv_file = self.cleaned_data.get("csv_file")
        if not csv_file:
            raise ValidationError(_("Please upload a CSV file."))

        if not csv_file.name.endswith(".csv"):
            raise ValidationError(_("File must be a CSV."))

        # Validate CSV content
        try:
            content = csv_file.read().decode("utf-8")
            csv_file.seek(0)  # Reset file pointer
            
            reader = csv.DictReader(io.StringIO(content))
            rows = list(reader)
            
            if not rows:
                raise ValidationError(_("CSV file is empty."))
            
            # Check required columns
            if "email" not in reader.fieldnames:
                raise ValidationError(_("CSV must contain an 'email' column."))
            
            # Validate at least one email
            valid_rows = 0
            for row in rows:
                if row.get("email", "").strip():
                    valid_rows += 1
            
            if valid_rows == 0:
                raise ValidationError(_("No valid email addresses found in CSV."))
                
        except UnicodeDecodeError:
            raise ValidationError(_("File encoding must be UTF-8."))
        except csv.Error:
            raise ValidationError(_("Invalid CSV format."))

        return csv_file


class SubscriberTagForm(forms.ModelForm):
    """Form for creating and editing subscriber tags."""

    class Meta:
        model = SubscriberTag
        fields = ["name", "description", "color"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "dashboard-input",
                "placeholder": _("Tag name"),
            }),
            "description": forms.Textarea(attrs={
                "class": "dashboard-textarea",
                "placeholder": _("Optional description"),
                "rows": 3,
            }),
            "color": forms.TextInput(attrs={
                "class": "dashboard-input",
                "type": "color",
            }),
        }


class SubscriberSegmentForm(forms.ModelForm):
    """Form for creating and editing subscriber segments."""

    class Meta:
        model = SubscriberSegment
        fields = ["name", "description", "tags"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "dashboard-input",
                "placeholder": _("Segment name"),
            }),
            "description": forms.Textarea(attrs={
                "class": "dashboard-textarea",
                "placeholder": _("Optional description"),
                "rows": 3,
            }),
            "tags": forms.CheckboxSelectMultiple(),
        }


class SubscriberEditForm(forms.ModelForm):
    """Form for editing subscriber details in admin."""

    class Meta:
        model = NewsletterSubscriber
        fields = ["email", "language", "status", "is_active", "is_confirmed"]
        widgets = {
            "email": forms.EmailInput(attrs={
                "class": "dashboard-input",
            }),
            "language": forms.Select(attrs={
                "class": "dashboard-input",
            }),
            "status": forms.Select(attrs={
                "class": "dashboard-input",
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "dashboard-checkbox",
            }),
            "is_confirmed": forms.CheckboxInput(attrs={
                "class": "dashboard-checkbox",
            }),
        }
