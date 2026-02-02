"""
Coupon forms for dashboard CRUD operations.
"""
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from tech_articles.billing.models import Coupon


class CouponForm(forms.ModelForm):
    """Form for creating and editing discount coupons."""

    class Meta:
        model = Coupon
        fields = [
            "code",
            "coupon_type",
            "value_percent",
            "value_amount",
            "currency",
            "max_uses",
            "expires_at",
            "is_active",
        ]
        widgets = {
            "code": forms.TextInput(
                attrs={
                    "class": "dashboard-input",
                    "placeholder": _("COUPON_CODE"),
                    "style": "text-transform: uppercase;",
                }
            ),
            "coupon_type": forms.Select(attrs={"class": "dashboard-input"}),
            "value_percent": forms.NumberInput(
                attrs={
                    "class": "dashboard-input",
                    "min": "1",
                    "max": "100",
                    "placeholder": _("e.g., 20 for 20%"),
                }
            ),
            "value_amount": forms.NumberInput(
                attrs={
                    "class": "dashboard-input",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": _("e.g., 10.00"),
                }
            ),
            "currency": forms.Select(attrs={"class": "dashboard-input"}),
            "max_uses": forms.NumberInput(
                attrs={
                    "class": "dashboard-input",
                    "min": "1",
                    "placeholder": _("Leave empty for unlimited"),
                }
            ),
            "expires_at": forms.DateTimeInput(
                attrs={
                    "class": "dashboard-input",
                    "type": "datetime-local",
                }
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "dashboard-checkbox"}),
        }

    def clean_code(self):
        """Convert code to uppercase."""
        code = self.cleaned_data.get("code")
        if code:
            code = code.upper()
        return code

    def clean(self):
        """Validate coupon value fields."""
        cleaned_data = super().clean()
        coupon_type = cleaned_data.get("coupon_type")
        value_percent = cleaned_data.get("value_percent")
        value_amount = cleaned_data.get("value_amount")

        if coupon_type == "percent":
            if not value_percent:
                raise ValidationError(
                    {"value_percent": _("Percentage value is required for percent coupons.")}
                )
            if value_amount:
                cleaned_data["value_amount"] = None

        elif coupon_type == "amount":
            if not value_amount:
                raise ValidationError(
                    {"value_amount": _("Amount value is required for fixed amount coupons.")}
                )
            if value_percent:
                cleaned_data["value_percent"] = None

        return cleaned_data
