"""
Subscriber tag forms for admin dashboard.
"""
from django import forms
from django.utils.translation import gettext_lazy as _

from tech_articles.newsletter.models import SubscriberTag


class SubscriberTagForm(forms.ModelForm):
    """Form for creating and editing subscriber tags."""

    class Meta:
        model = SubscriberTag
        fields = ["name", "description", "color"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "dashboard-input",
                "placeholder": _("Enter tag name"),
                "autocomplete": "off",
            }),
            "description": forms.Textarea(attrs={
                "class": "dashboard-textarea",
                "placeholder": _("Optional description for this tag"),
                "rows": 3,
            }),
            "color": forms.TextInput(attrs={
                "class": "dashboard-input",
                "type": "color",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["description"].required = False

    def clean_name(self):
        name = self.cleaned_data.get("name", "").strip()
        if not name:
            raise forms.ValidationError(_("Tag name is required."))

        # Check for duplicates excluding current instance
        qs = SubscriberTag.objects.filter(name__iexact=name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(_("A tag with this name already exists."))

        return name
