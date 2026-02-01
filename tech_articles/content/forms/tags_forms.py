"""
Tag forms for dashboard CRUD operations.
"""
from django import forms
from django.utils.translation import gettext_lazy as _

from tech_articles.content.models import Tag


class TagForm(forms.ModelForm):
    """Form for creating and updating tags."""

    class Meta:
        model = Tag
        fields = ["name", "slug"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "dashboard-input",
                "placeholder": _("Enter tag name"),
                "autocomplete": "off",
            }),
            "slug": forms.TextInput(attrs={
                "class": "dashboard-input",
                "placeholder": _("URL-friendly identifier (auto-generated if empty)"),
                "autocomplete": "off",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["slug"].required = False

    def clean_name(self):
        name = self.cleaned_data.get("name", "").strip()
        if not name:
            raise forms.ValidationError(_("Tag name is required."))

        # Check for duplicates excluding current instance
        qs = Tag.objects.filter(name__iexact=name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(_("A tag with this name already exists."))

        return name

    def clean_slug(self):
        slug = self.cleaned_data.get("slug", "").strip()
        if slug:
            # Check for duplicates excluding current instance
            qs = Tag.objects.filter(slug=slug)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError(_("A tag with this slug already exists."))
        return slug
