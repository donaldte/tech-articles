from __future__ import annotations

from decimal import Decimal
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from tech_articles.common.models import UUIDModel, TimeStampedModel
from tech_articles.content.models import Article
from tech_articles.utils.enums import PlanInterval, PaymentProvider, PaymentStatus, CouponType


class Plan(UUIDModel, TimeStampedModel):
    name = models.CharField(
        _("name"),
        max_length=100,
        unique=True,
        help_text=_("Plan name"),
    )
    slug = models.SlugField(
        _("slug"),
        max_length=120,
        unique=True,
        db_index=True,
        help_text=_("URL-friendly identifier"),
    )
    description = models.TextField(
        _("description"),
        blank=True,
        default="",
        help_text=_("Plan description"),
    )
    is_active = models.BooleanField(
        _("is active"),
        default=True,
        db_index=True,
        help_text=_("Whether the plan is available for purchase"),
    )
    is_popular = models.BooleanField(
        _("is popular"),
        default=False,
        help_text=_("Mark this plan as popular/highlighted"),
    )
    display_order = models.PositiveIntegerField(
        _("display order"),
        default=0,
        help_text=_("Order in which plans are displayed (lower numbers first)"),
    )

    price = models.DecimalField(
        _("price"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text=_("Plan price"),
    )
    currency = models.CharField(
        _("currency"),
        max_length=3,
        default="USD",
        help_text=_("Currency code (ISO 4217)"),
    )
    interval = models.CharField(
        _("billing interval"),
        max_length=10,
        choices=PlanInterval.choices,
        default=PlanInterval.MONTH,
        help_text=_("Billing period (monthly, yearly, etc.)"),
    )
    custom_interval_count = models.PositiveIntegerField(
        _("custom interval count"),
        null=True,
        blank=True,
        help_text=_("For custom intervals (e.g., every 3 months)"),
    )

    # Trial period
    trial_period_days = models.PositiveIntegerField(
        _("trial period (days)"),
        null=True,
        blank=True,
        help_text=_("Number of days for free trial"),
    )

    # Limits
    max_articles = models.PositiveIntegerField(
        _("max articles"),
        null=True,
        blank=True,
        help_text=_("Maximum number of articles accessible (null = unlimited)"),
    )
    max_resources = models.PositiveIntegerField(
        _("max resources"),
        null=True,
        blank=True,
        help_text=_("Maximum number of resources accessible (null = unlimited)"),
    )
    max_appointments = models.PositiveIntegerField(
        _("max appointments"),
        null=True,
        blank=True,
        help_text=_("Maximum number of appointments per month (null = unlimited)"),
    )

    features_json = models.TextField(
        _("features"),
        blank=True,
        default="",
        help_text=_("Plan features in JSON format"),
    )

    provider = models.CharField(
        _("payment provider"),
        max_length=20,
        choices=PaymentProvider.choices,
        default=PaymentProvider.STRIPE,
        help_text=_("Payment service provider"),
    )
    provider_price_id = models.CharField(
        _("provider price ID"),
        max_length=160,
        blank=True,
        default="",
        help_text=_("Stripe Price ID, PayPal plan ID, etc."),
    )

    class Meta:
        verbose_name = _("plan")
        verbose_name_plural = _("plans")
        ordering = ["display_order", "price"]
        indexes = [
            models.Index(fields=["is_active", "display_order"]),
            models.Index(fields=["is_active", "price"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.price} {self.currency}/{self.interval})"


class Subscription(UUIDModel, TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("user"),
        on_delete=models.CASCADE,
        related_name="subscriptions",
        help_text=_("Subscribed user"),
    )
    plan = models.ForeignKey(
        Plan,
        verbose_name=_("plan"),
        on_delete=models.PROTECT,
        related_name="subscriptions",
        help_text=_("Subscribed plan"),
    )

    provider = models.CharField(
        _("provider"),
        max_length=20,
        choices=PaymentProvider.choices,
        help_text=_("Payment service provider"),
    )
    provider_subscription_id = models.CharField(
        _("provider subscription ID"),
        max_length=160,
        blank=True,
        default="",
        help_text=_("External subscription ID (Stripe, PayPal, etc.)"),
    )
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        db_index=True,
        help_text=_("Subscription payment status"),
    )

    current_period_start = models.DateTimeField(
        _("current period start"),
        null=True,
        blank=True,
        help_text=_("Start of current billing period"),
    )
    current_period_end = models.DateTimeField(
        _("current period end"),
        null=True,
        blank=True,
        db_index=True,
        help_text=_("End of current billing period"),
    )
    cancel_at_period_end = models.BooleanField(
        _("cancel at period end"),
        default=False,
        help_text=_("Cancel subscription at the end of period"),
    )

    class Meta:
        verbose_name = _("subscription")
        verbose_name_plural = _("subscriptions")
        indexes = [
            models.Index(fields=["user", "status", "current_period_end"]),
        ]

    @property
    def is_active(self) -> bool:
        return self.status == PaymentStatus.SUCCEEDED and (self.current_period_end is None or self.current_period_end > timezone.now())

    def __str__(self) -> str:
        return f"{self.user_id} - {self.plan.name} ({self.status})"


class Purchase(UUIDModel, TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("user"),
        on_delete=models.CASCADE,
        related_name="purchases",
        help_text=_("Purchasing user"),
    )
    article = models.ForeignKey(
        Article,
        verbose_name=_("article"),
        on_delete=models.PROTECT,
        related_name="purchases",
        help_text=_("Purchased article"),
    )

    provider = models.CharField(
        _("provider"),
        max_length=20,
        choices=PaymentProvider.choices,
        help_text=_("Payment service provider"),
    )
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        db_index=True,
        help_text=_("Payment status"),
    )

    amount = models.DecimalField(
        _("amount"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text=_("Purchase amount"),
    )
    currency = models.CharField(
        _("currency"),
        max_length=3,
        default="USD",
        help_text=_("Currency code (ISO 4217)"),
    )

    provider_payment_id = models.CharField(
        _("provider payment ID"),
        max_length=160,
        blank=True,
        default="",
        help_text=_("Stripe PaymentIntent ID, PayPal order ID, etc."),
    )

    class Meta:
        verbose_name = _("purchase")
        verbose_name_plural = _("purchases")
        unique_together = [("user", "article")]
        indexes = [
            models.Index(fields=["user", "status"]),
        ]

    def __str__(self) -> str:
        return f"Purchase {self.user_id} -> {self.article_id} ({self.status})"


class Coupon(UUIDModel, TimeStampedModel):
    code = models.CharField(
        _("code"),
        max_length=40,
        unique=True,
        db_index=True,
        help_text=_("Coupon code"),
    )
    coupon_type = models.CharField(
        _("type"),
        max_length=10,
        choices=CouponType.choices,
        help_text=_("Discount type (percentage or fixed amount)"),
    )
    value_percent = models.PositiveIntegerField(
        _("percentage value"),
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text=_("Discount percentage (1-100)"),
    )
    value_amount = models.DecimalField(
        _("fixed amount value"),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text=_("Fixed discount amount"),
    )

    currency = models.CharField(
        _("currency"),
        max_length=3,
        default="USD",
        help_text=_("Currency code (ISO 4217)"),
    )
    max_uses = models.PositiveIntegerField(
        _("max uses"),
        null=True,
        blank=True,
        help_text=_("Maximum times the coupon can be used"),
    )
    used_count = models.PositiveIntegerField(
        _("used count"),
        default=0,
        help_text=_("Current usage count"),
    )
    expires_at = models.DateTimeField(
        _("expires at"),
        null=True,
        blank=True,
        db_index=True,
        help_text=_("Coupon expiration date and time"),
    )
    is_active = models.BooleanField(
        _("is active"),
        default=True,
        db_index=True,
        help_text=_("Whether the coupon is currently active"),
    )

    class Meta:
        verbose_name = _("coupon")
        verbose_name_plural = _("coupons")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["code", "is_active"]),
            models.Index(fields=["expires_at", "is_active"]),
        ]

    def __str__(self) -> str:
        return self.code


class PlanFeature(UUIDModel, TimeStampedModel):
    """Features associated with a subscription plan."""
    plan = models.ForeignKey(
        Plan,
        verbose_name=_("plan"),
        on_delete=models.CASCADE,
        related_name="plan_features",
        help_text=_("Associated plan"),
    )
    name = models.CharField(
        _("feature name"),
        max_length=255,
        help_text=_("Name of the feature"),
    )
    description = models.TextField(
        _("description"),
        blank=True,
        default="",
        help_text=_("Detailed description of the feature"),
    )
    is_included = models.BooleanField(
        _("is included"),
        default=True,
        help_text=_("Whether this feature is included or excluded"),
    )
    display_order = models.PositiveIntegerField(
        _("display order"),
        default=0,
        help_text=_("Order in which features are displayed"),
    )

    class Meta:
        verbose_name = _("plan feature")
        verbose_name_plural = _("plan features")
        ordering = ["plan", "display_order"]
        unique_together = [("plan", "name")]

    def __str__(self) -> str:
        return f"{self.plan.name} - {self.name}"


class PlanHistory(UUIDModel, TimeStampedModel):
    """History of changes made to subscription plans."""
    plan = models.ForeignKey(
        Plan,
        verbose_name=_("plan"),
        on_delete=models.CASCADE,
        related_name="history_records",
        help_text=_("Associated plan"),
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("changed by"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text=_("User who made the change"),
    )
    change_type = models.CharField(
        _("change type"),
        max_length=20,
        help_text=_("Type of change (created, updated, deleted, etc.)"),
    )
    changes = models.TextField(
        _("changes"),
        help_text=_("Description of changes made"),
    )
    snapshot = models.JSONField(
        _("snapshot"),
        null=True,
        blank=True,
        help_text=_("Full snapshot of plan data at time of change"),
    )

    class Meta:
        verbose_name = _("plan history")
        verbose_name_plural = _("plan histories")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["plan", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.plan.name} - {self.change_type} at {self.created_at}"
