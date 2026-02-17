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
                },
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show published articles in the dropdown
        qs = Article.objects.filter(status="published").order_by("-published_at")
        for name in ("first_feature", "second_feature", "third_feature"):
            self.fields[name].queryset = qs
            # All fields are optional
            self.fields[name].required = False
            # Remove the empty '---------' option
            if hasattr(self.fields[name], "empty_label"):
                self.fields[name].empty_label = None
