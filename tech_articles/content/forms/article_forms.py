"""
Article forms for dashboard CRUD operations.
"""
from django import forms
from django.utils.translation import gettext_lazy as _

from tech_articles.content.models import Article, Category


# Currency choices for article pricing
CURRENCY_CHOICES = [
    ("USD", _("USD - US Dollar")),
    ("EUR", _("EUR - Euro")),
    ("GBP", _("GBP - British Pound")),
    ("XAF", _("XAF - CFA Franc")),
]


class ArticleSetupForm(forms.ModelForm):
    """Form for basic article setup (Title + Language only)."""

    class Meta:
        model = Article
        fields = ["title", "language"]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "dashboard-input w-full",
                "placeholder": _("E.g.: Introduction to DevOps Practices"),
                "autocomplete": "off",
                "required": True,
                "maxlength": 150,
            }),
            "language": forms.Select(attrs={
                "class": "dashboard-select w-full",
            }),
        }

    def clean_title(self):
        title = self.cleaned_data.get("title", "").strip()
        if not title:
            raise forms.ValidationError(_("Article title is required."))
        return title


class ArticleQuickCreateForm(forms.ModelForm):
    """Form for quick article creation (Setup flow)."""

    class Meta:
        model = Article
        fields = ["title", "categories", "language"]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "dashboard-input w-full",
                "placeholder": _("Enter article title"),
                "autocomplete": "off",
                "required": True,
            }),
            "categories": forms.SelectMultiple(attrs={
                "class": "dashboard-select w-full",
            }),
            "language": forms.Select(attrs={
                "class": "dashboard-select w-full",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["categories"].queryset = Category.objects.filter(is_active=True)
        self.fields["categories"].required = False

    def clean_title(self):
        title = self.cleaned_data.get("title", "").strip()
        if not title:
            raise forms.ValidationError(_("Article title is required."))
        return title


class ArticleDetailsForm(forms.ModelForm):
    """Form for editing article details (Mini Dashboard - Details tab)."""

    class Meta:
        model = Article
        fields = ["title", "language", "summary", "difficulty", "status"]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "dashboard-input w-full",
                "placeholder": _("Enter article title"),
                "autocomplete": "off",
            }),
            "language": forms.Select(attrs={
                "class": "dashboard-select w-full",
            }),
            "summary": forms.Textarea(attrs={
                "class": "dashboard-textarea w-full",
                "placeholder": _("Brief article summary"),
                "rows": 4,
            }),
            "difficulty": forms.Select(attrs={
                "class": "dashboard-select w-full",
            }),
            "status": forms.Select(attrs={
                "class": "dashboard-select w-full",
            }),
        }

    def clean_title(self):
        title = self.cleaned_data.get("title", "").strip()
        if not title:
            raise forms.ValidationError(_("Article title is required."))
        return title


class ArticleSEOForm(forms.ModelForm):
    """Form for editing article SEO settings (Mini Dashboard - SEO tab)."""

    class Meta:
        model = Article
        fields = ["seo_title", "seo_description", "canonical_url", "cover_image_key", "cover_alt_text"]
        widgets = {
            "seo_title": forms.TextInput(attrs={
                "class": "dashboard-input w-full",
                "placeholder": _("Meta title for search engines (max 70 characters)"),
                "autocomplete": "off",
                "maxlength": 70,
            }),
            "seo_description": forms.Textarea(attrs={
                "class": "dashboard-textarea w-full",
                "placeholder": _("Meta description for search engines (max 160 characters)"),
                "rows": 3,
                "maxlength": 160,
            }),
            "canonical_url": forms.URLInput(attrs={
                "class": "dashboard-input w-full",
                "placeholder": _("https://example.com/article"),
            }),
            "cover_image_key": forms.TextInput(attrs={
                "class": "dashboard-input w-full",
                "placeholder": _("S3 key/path for cover image"),
                "autocomplete": "off",
            }),
            "cover_alt_text": forms.TextInput(attrs={
                "class": "dashboard-input w-full",
                "placeholder": _("Descriptive text for the cover image"),
                "autocomplete": "off",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False


class ArticlePricingForm(forms.ModelForm):
    """Form for editing article pricing (Mini Dashboard - Pricing tab)."""

    class Meta:
        model = Article
        fields = ["access_type", "price", "currency"]
        widgets = {
            "access_type": forms.Select(attrs={
                "class": "dashboard-select w-full",
            }),
            "price": forms.NumberInput(attrs={
                "class": "dashboard-input w-full",
                "placeholder": "0.00",
                "step": "0.01",
                "min": "0",
            }),
            "currency": forms.Select(attrs={
                "class": "dashboard-select w-full",
            }, choices=CURRENCY_CHOICES),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["price"].required = False

    def clean(self):
        cleaned_data = super().clean()
        access_type = cleaned_data.get("access_type")
        price = cleaned_data.get("price")

        if access_type == "paid" and (price is None or price <= 0):
            self.add_error("price", _("Price must be greater than 0 for paid articles."))

        return cleaned_data


class ArticleForm(forms.ModelForm):
    """Form for creating and updating articles."""

    class Meta:
        model = Article
        fields = [
            "title", "slug", "language", "status", "difficulty", "access_type", "price", "currency",
            "seo_title", "seo_description", "canonical_url", "summary", "cover_image_key",
            "cover_alt_text", "reading_time_minutes", "youtube_url", "youtube_start_seconds",
            "categories", "tags", "author", "published_at"
        ]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "dashboard-input",
                "placeholder": _("Enter article title"),
                "autocomplete": "off",
            }),
            "slug": forms.TextInput(attrs={
                "class": "dashboard-input",
                "placeholder": _("URL-friendly identifier (auto-generated if empty)"),
                "autocomplete": "off",
            }),
            "language": forms.Select(attrs={
                "class": "dashboard-select",
            }),
            "status": forms.Select(attrs={
                "class": "dashboard-select",
            }),
            "difficulty": forms.Select(attrs={
                "class": "dashboard-select",
            }),
            "access_type": forms.Select(attrs={
                "class": "dashboard-select",
            }),
            "price": forms.NumberInput(attrs={
                "class": "dashboard-input",
                "placeholder": "0.00",
                "step": "0.01",
            }),
            "currency": forms.TextInput(attrs={
                "class": "dashboard-input",
                "placeholder": "USD",
            }),
            "seo_title": forms.TextInput(attrs={
                "class": "dashboard-input",
                "placeholder": _("Meta title for search engines"),
                "autocomplete": "off",
            }),
            "seo_description": forms.TextInput(attrs={
                "class": "dashboard-input",
                "placeholder": _("Meta description for search engines"),
                "autocomplete": "off",
            }),
            "canonical_url": forms.URLInput(attrs={
                "class": "dashboard-input",
                "placeholder": _("Canonical URL for duplicate content"),
            }),
            "summary": forms.Textarea(attrs={
                "class": "dashboard-textarea",
                "placeholder": _("Brief article summary"),
                "rows": 3,
            }),
            "cover_image_key": forms.TextInput(attrs={
                "class": "dashboard-input",
                "placeholder": _("S3 key/path for cover image"),
                "autocomplete": "off",
            }),
            "cover_alt_text": forms.TextInput(attrs={
                "class": "dashboard-input",
                "placeholder": _("Alternative text for cover image"),
                "autocomplete": "off",
            }),
            "reading_time_minutes": forms.NumberInput(attrs={
                "class": "dashboard-input",
                "placeholder": "0",
            }),
            "youtube_url": forms.URLInput(attrs={
                "class": "dashboard-input",
                "placeholder": _("Optional YouTube video URL"),
            }),
            "youtube_start_seconds": forms.NumberInput(attrs={
                "class": "dashboard-input",
                "placeholder": "0",
            }),
            "categories": forms.SelectMultiple(attrs={
                "class": "dashboard-select",
            }),
            "tags": forms.SelectMultiple(attrs={
                "class": "dashboard-select",
            }),
            "author": forms.Select(attrs={
                "class": "dashboard-select",
            }),
            "published_at": forms.DateTimeInput(attrs={
                "class": "dashboard-input",
                "type": "datetime-local",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["slug"].required = False
        self.fields["price"].required = False
        self.fields["seo_title"].required = False
        self.fields["seo_description"].required = False
        self.fields["canonical_url"].required = False
        self.fields["summary"].required = False
        self.fields["cover_image_key"].required = False
        self.fields["cover_alt_text"].required = False
        self.fields["youtube_url"].required = False
        self.fields["author"].required = False
        self.fields["published_at"].required = False

    def clean_title(self):
        title = self.cleaned_data.get("title", "").strip()
        if not title:
            raise forms.ValidationError(_("Article title is required."))
        return title

    def clean_slug(self):
        slug = self.cleaned_data.get("slug", "").strip()
        if slug:
            # Check for duplicates excluding current instance
            qs = Article.objects.filter(slug=slug)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError(_("An article with this slug already exists."))
        return slug
