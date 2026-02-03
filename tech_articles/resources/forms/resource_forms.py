"""
Resource document forms for dashboard CRUD operations.
"""
from django import forms
from django.utils.translation import gettext_lazy as _

from tech_articles.resources.models import ResourceDocument


class ResourceDocumentForm(forms.ModelForm):
    """Form for creating and updating resource documents."""

    class Meta:
        model = ResourceDocument
        fields = ["title", "description", "file_key", "access_level", "article", "category", "watermark_enabled"]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "dashboard-input",
                "placeholder": _("Enter resource title"),
                "autocomplete": "off",
            }),
            "description": forms.Textarea(attrs={
                "class": "dashboard-textarea",
                "placeholder": _("Optional description for this resource"),
                "rows": 3,
            }),
            "file_key": forms.TextInput(attrs={
                "class": "dashboard-input",
                "placeholder": _("S3 key/path to the document file"),
                "autocomplete": "off",
            }),
            "access_level": forms.Select(attrs={
                "class": "dashboard-select",
            }),
            "article": forms.Select(attrs={
                "class": "dashboard-select",
            }),
            "category": forms.Select(attrs={
                "class": "dashboard-select",
            }),
            "watermark_enabled": forms.CheckboxInput(attrs={
                "class": "dashboard-checkbox",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["description"].required = False
        self.fields["article"].required = False
        self.fields["category"].required = False

    def clean_title(self):
        title = self.cleaned_data.get("title", "").strip()
        if not title:
            raise forms.ValidationError(_("Resource title is required."))
        return title

    def clean_file_key(self):
        file_key = self.cleaned_data.get("file_key", "").strip()
        if not file_key:
            raise forms.ValidationError(_("File key is required."))
        return file_key
