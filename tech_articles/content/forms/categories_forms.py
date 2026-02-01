"""
Category forms for dashboard CRUD operations.
"""
from django import forms
from django.utils.translation import gettext_lazy as _

from tech_articles.content.models import Category


class CategoryForm(forms.ModelForm):
    """Form for creating and updating categories."""

    class Meta:
        model = Category
        fields = ["name", "slug", "description", "is_active", "sort_order"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "dashboard-input",
                "placeholder": _("Enter category name"),
                "autocomplete": "off",
            }),
            "slug": forms.TextInput(attrs={
                "class": "dashboard-input",
                "placeholder": _("URL-friendly identifier (auto-generated if empty)"),
                "autocomplete": "off",
            }),
            "description": forms.Textarea(attrs={
                "class": "dashboard-textarea",
                "placeholder": _("Optional description for this category"),
                "rows": 3,
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "dashboard-checkbox",
            }),
            "sort_order": forms.NumberInput(attrs={
                "class": "dashboard-input",
                "placeholder": "0",
                "min": 0,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["slug"].required = False
        self.fields["description"].required = False

    def clean_name(self):
        name = self.cleaned_data.get("name", "").strip()
        if not name:
            raise forms.ValidationError(_("Category name is required."))

        # Check for duplicates excluding current instance
        qs = Category.objects.filter(name__iexact=name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(_("A category with this name already exists."))

        return name

    def clean_slug(self):
        slug = self.cleaned_data.get("slug", "").strip()
        if slug:
            # Check for duplicates excluding current instance
            qs = Category.objects.filter(slug=slug)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError(_("A category with this slug already exists."))
        return slug
