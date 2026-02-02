from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify

from .models import Plan, PlanFeature, Coupon


class PlanForm(forms.ModelForm):
    """Form for creating and editing subscription plans."""

    class Meta:
        model = Plan
        fields = [
            "name",
            "slug",
            "description",
            "price",
            "currency",
            "interval",
            "custom_interval_count",
            "trial_period_days",
            "max_articles",
            "max_resources",
            "max_appointments",
            "is_active",
            "is_popular",
            "display_order",
            "provider",
            "provider_price_id",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "dashboard-input",
                    "placeholder": _("Enter plan name"),
                }
            ),
            "slug": forms.TextInput(
                attrs={
                    "class": "dashboard-input",
                    "placeholder": _("auto-generated-slug"),
                    "required": "False",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "dashboard-textarea",
                    "rows": 4,
                    "placeholder": _("Enter plan description"),
                }
            ),
            "price": forms.NumberInput(
                attrs={
                    "class": "dashboard-input",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "0.00",
                }
            ),
            "currency": forms.Select(attrs={"class": "dashboard-input"}),
            "interval": forms.Select(attrs={"class": "dashboard-input"}),
            "custom_interval_count": forms.NumberInput(
                attrs={
                    "class": "dashboard-input",
                    "min": "1",
                    "placeholder": _("e.g., 3 for 3 months"),
                }
            ),
            "trial_period_days": forms.NumberInput(
                attrs={
                    "class": "dashboard-input",
                    "min": "0",
                    "placeholder": _("e.g., 14 for 14 days"),
                }
            ),
            "max_articles": forms.NumberInput(
                attrs={
                    "class": "dashboard-input",
                    "min": "0",
                    "placeholder": _("Leave empty for unlimited"),
                }
            ),
            "max_resources": forms.NumberInput(
                attrs={
                    "class": "dashboard-input",
                    "min": "0",
                    "placeholder": _("Leave empty for unlimited"),
                }
            ),
            "max_appointments": forms.NumberInput(
                attrs={
                    "class": "dashboard-input",
                    "min": "0",
                    "placeholder": _("Leave empty for unlimited"),
                }
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "dashboard-checkbox"}),
            "is_popular": forms.CheckboxInput(attrs={"class": "dashboard-checkbox"}),
            "display_order": forms.NumberInput(
                attrs={
                    "class": "dashboard-input",
                    "min": "0",
                }
            ),
            "provider": forms.Select(attrs={"class": "dashboard-input"}),
            "provider_price_id": forms.TextInput(
                attrs={
                    "class": "dashboard-input",
                    "placeholder": _("Provider-specific price ID"),
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["slug"].required = False
        self.fields["description"].required = False

    def clean_slug(self):
        slug = self.cleaned_data.get("slug", "").strip()
        if slug:
            # Check for duplicates excluding current instance
            qs = Plan.objects.filter(slug=slug)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError(_("A plan with this slug already exists."))
        return slug

    def clean(self):
        """Validate custom interval fields."""
        cleaned_data = super().clean()
        interval = cleaned_data.get("interval")
        custom_interval_count = cleaned_data.get("custom_interval_count")

        if interval == "custom" and not custom_interval_count:
            raise ValidationError(
                {
                    "custom_interval_count": _(
                        "Custom interval count is required when using custom interval."
                    )
                }
            )

        return cleaned_data


class PlanFeatureForm(forms.ModelForm):
    """Form for adding features to a plan."""

    class Meta:
        model = PlanFeature
        fields = ["name", "description", "is_included", "display_order"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "dashboard-input",
                    "placeholder": _("Feature name"),
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "dashboard-textarea",
                    "rows": 2,
                    "placeholder": _("Feature description (optional)"),
                }
            ),
            "is_included": forms.CheckboxInput(attrs={"class": "dashboard-checkbox"}),
            "display_order": forms.NumberInput(
                attrs={
                    "class": "dashboard-input",
                    "min": "0",
                }
            ),
        }


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
