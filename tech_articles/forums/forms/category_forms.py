"""
Forum category forms for dashboard CRUD operations.
"""

from django import forms
from django.utils.translation import gettext_lazy as _

from tech_articles.forums.models import ForumCategory


class ForumCategoryForm(forms.ModelForm):
    """Form for creating and editing forum categories."""

    class Meta:
        model = ForumCategory
        fields = [
            "name",
            "slug",
            "description",
            "svg_icon",
            "is_active",
            "requires_subscription",
            "requires_admin_approval",
            "is_purchasable",
            "purchase_price",
            "purchase_currency",
            "display_order",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "dashboard-input",
                    "placeholder": _("Enter category name"),
                }
            ),
            "slug": forms.TextInput(
                attrs={
                    "class": "dashboard-input",
                    "placeholder": _("auto-generated-slug"),
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "dashboard-textarea",
                    "rows": 3,
                    "placeholder": _("Short description of the category"),
                }
            ),
            "svg_icon": forms.Textarea(
                attrs={
                    "class": "dashboard-textarea font-mono",
                    "rows": 8,
                    "placeholder": _(
                        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
                        'fill="currentColor">...</svg>'
                    ),
                }
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "dashboard-checkbox"}),
            "requires_subscription": forms.CheckboxInput(
                attrs={"class": "dashboard-checkbox"}
            ),
            "requires_admin_approval": forms.CheckboxInput(
                attrs={"class": "dashboard-checkbox"}
            ),
            "is_purchasable": forms.CheckboxInput(
                attrs={"class": "dashboard-checkbox"}
            ),
            "purchase_price": forms.NumberInput(
                attrs={
                    "class": "dashboard-input",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "0.00",
                }
            ),
            "purchase_currency": forms.Select(attrs={"class": "dashboard-select"}),
            "display_order": forms.NumberInput(
                attrs={
                    "class": "dashboard-input",
                    "min": "0",
                }
            ),
        }
        labels = {
            "svg_icon": _("SVG icon (raw markup)"),
        }
        help_texts = {
            "svg_icon": _(
                "Paste the raw SVG markup. Replace hard-coded colour values with "
                "currentColor so the icon adapts to dark/light mode automatically."
            ),
            "purchase_price": _(
                "Required when 'Is purchasable' is enabled."
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        is_purchasable = cleaned_data.get("is_purchasable")
        purchase_price = cleaned_data.get("purchase_price")

        if is_purchasable and not purchase_price:
            self.add_error(
                "purchase_price",
                _("A purchase price is required when the category is purchasable."),
            )

        return cleaned_data
