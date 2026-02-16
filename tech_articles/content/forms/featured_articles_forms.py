"""
Featured Articles form for dashboard management.
"""

from django import forms
from django.utils.translation import gettext_lazy as _

from tech_articles.content.models import FeaturedArticles, Article


class FeaturedArticlesForm(forms.ModelForm):
    """Form for managing featured articles displayed on the homepage."""

    class Meta:
        model = FeaturedArticles
        fields = ["first_feature", "second_feature", "third_feature"]
        widgets = {
            "first_feature": forms.Select(
                attrs={
                    "class": "w-full",
                    "placeholder": _("Select first featured article"),
                }
            ),
            "second_feature": forms.Select(
                attrs={
                    "class": "w-full",
                    "placeholder": _("Select second featured article"),
                }
            ),
            "third_feature": forms.Select(
                attrs={
                    "class": "w-full",
                    "placeholder": _("Select third featured article"),
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show published articles in the dropdown
        self.fields["first_feature"].queryset = Article.objects.filter(
            status="published"
        ).order_by("-published_at")
        self.fields["second_feature"].queryset = Article.objects.filter(
            status="published"
        ).order_by("-published_at")
        self.fields["third_feature"].queryset = Article.objects.filter(
            status="published"
        ).order_by("-published_at")

        # All fields are optional
        self.fields["first_feature"].required = False
        self.fields["second_feature"].required = False
        self.fields["third_feature"].required = False
