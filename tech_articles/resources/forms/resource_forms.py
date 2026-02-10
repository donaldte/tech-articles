"""
Resource document forms for dashboard CRUD operations.
"""
from django import forms
from django.utils.translation import gettext_lazy as _

from tech_articles.resources.models import ResourceDocument
from tech_articles.content.models import Article, Category


class ResourceDocumentForm(forms.ModelForm):
    """Form for creating and updating resource documents."""

    class Meta:
        model = ResourceDocument
        fields = [
            "title",
            "description",
            "category",
            "article",
            "access_level",
            "watermark_enabled",
            "is_active",
        ]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "dashboard-input w-full",
                "placeholder": _("Enter resource title"),
                "autocomplete": "off",
            }),
            "description": forms.Textarea(attrs={
                "class": "dashboard-input w-full",
                "placeholder": _("Optional description for this resource"),
                "rows": 4,
            }),
            "category": forms.Select(attrs={
                "class": "dashboard-select w-full",
            }),
            "article": forms.Select(attrs={
                "class": "dashboard-select w-full",
            }),
            "access_level": forms.Select(attrs={
                "class": "dashboard-select w-full",
            }),
            "watermark_enabled": forms.CheckboxInput(attrs={
                "class": "dashboard-checkbox",
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "dashboard-checkbox",
            }),
        }

    def __init__(self, *args, **kwargs):
        # Extract optional parameters
        show_article = kwargs.pop('show_article', True)
        category_filter = kwargs.pop('category_filter', None)

        super().__init__(*args, **kwargs)

        # Configure field requirements
        self.fields["description"].required = False
        self.fields["article"].required = False
        self.fields["category"].required = False

        # Configure article field visibility
        if not show_article:
            self.fields.pop('article', None)

        # Filter articles by category if specified
        if category_filter and 'article' in self.fields:
            self.fields['article'].queryset = Article.objects.filter(
                categories=category_filter
            ).distinct()

        # Set initial queryset for articles if not filtered
        if 'article' in self.fields and not category_filter:
            self.fields['article'].queryset = Article.objects.all().order_by('-created_at')

    def clean_title(self):
        title = self.cleaned_data.get("title", "").strip()
        if not title:
            raise forms.ValidationError(_("Resource title is required."))
        return title


class ResourceDocumentPopupForm(forms.ModelForm):
    """
    Simplified form for creating resource documents in popup mode
    (when called from article creation/editing)
    """

    class Meta:
        model = ResourceDocument
        fields = [
            "title",
            "description",
            "category",
            "access_level",
            "watermark_enabled",
        ]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "dashboard-input w-full",
                "placeholder": _("Enter resource title"),
                "autocomplete": "off",
            }),
            "description": forms.Textarea(attrs={
                "class": "dashboard-input w-full",
                "placeholder": _("Describe this resource..."),
                "rows": 4,
            }),
            "category": forms.Select(attrs={
                "class": "dashboard-select w-full",
            }),
            "access_level": forms.Select(attrs={
                "class": "dashboard-select w-full",
            }),
            "watermark_enabled": forms.CheckboxInput(attrs={
                "class": "dashboard-checkbox",
            }),
        }

    def __init__(self, *args, **kwargs):
        # Get article categories from popup parameters
        article_categories = kwargs.pop('article_categories', None)

        super().__init__(*args, **kwargs)

        # Category is optional
        self.fields["description"].required = False
        self.fields["category"].required = False

        # Filter categories if article categories provided
        if article_categories:
            self.fields["category"].queryset = Category.objects.filter(
                id__in=article_categories
            )

    def clean_title(self):
        title = self.cleaned_data.get("title", "").strip()
        if not title:
            raise forms.ValidationError(_("Resource title is required."))
        return title

