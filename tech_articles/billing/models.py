from __future__ import annotations

from decimal import Decimal
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

from tech_articles.common.models import UUIDModel, TimeStampedModel
from tech_articles.content.models import Article
from tech_articles.utils.enums import PlanInterval, PaymentProvider, PaymentStatus, CouponType


class Plan(UUIDModel, TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))])
    currency = models.CharField(max_length=3, default="USD")
    interval = models.CharField(max_length=10, choices=PlanInterval.choices, default=PlanInterval.MONTH)

    features_json = models.TextField(blank=True, default="")  # can store serialized json features

    provider = models.CharField(max_length=20, choices=PaymentProvider.choices, default=PaymentProvider.STRIPE)
    provider_price_id = models.CharField(max_length=160, blank=True, default="", help_text="Stripe Price ID, etc.")

    class Meta:
        ordering = ["price"]

    def __str__(self) -> str:
        return f"{self.name} ({self.price} {self.currency}/{self.interval})"


class Subscription(UUIDModel, TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscriptions")
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name="subscriptions")

    provider = models.CharField(max_length=20, choices=PaymentProvider.choices)
    provider_subscription_id = models.CharField(max_length=160, blank=True, default="")
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING, db_index=True)

    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True, db_index=True)
    cancel_at_period_end = models.BooleanField(default=False)

    class Meta:
        indexes = [models.Index(fields=["user", "status", "current_period_end"])]

    @property
    def is_active(self) -> bool:
        return self.status == PaymentStatus.SUCCEEDED and (self.current_period_end is None or self.current_period_end > timezone.now())

    def __str__(self) -> str:
        return f"{self.user_id} - {self.plan.name} ({self.status})"


class Purchase(UUIDModel, TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="purchases")
    article = models.ForeignKey(Article, on_delete=models.PROTECT, related_name="purchases")

    provider = models.CharField(max_length=20, choices=PaymentProvider.choices)
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING, db_index=True)

    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))])
    currency = models.CharField(max_length=3, default="USD")

    provider_payment_id = models.CharField(max_length=160, blank=True, default="", help_text="Stripe PaymentIntent ID, PayPal order ID, etc.")

    class Meta:
        unique_together = [("user", "article")]
        indexes = [models.Index(fields=["user", "status"])]

    def __str__(self) -> str:
        return f"Purchase {self.user_id} -> {self.article_id} ({self.status})"


class Coupon(UUIDModel, TimeStampedModel):
    code = models.CharField(max_length=40, unique=True, db_index=True)
    coupon_type = models.CharField(max_length=10, choices=CouponType.choices)
    value_percent = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(100)])
    value_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(Decimal("0.00"))])

    currency = models.CharField(max_length=3, default="USD")
    max_uses = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)
    expires_at = models.DateTimeField(null=True, blank=True, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    def __str__(self) -> str:
        return self.code
