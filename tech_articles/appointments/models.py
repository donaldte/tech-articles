from __future__ import annotations

from decimal import Decimal
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone

from tech_articles.common.models import UUIDModel, TimeStampedModel
from tech_articles.utils.enums import WeekdayChoices, AppointmentStatus, PaymentStatus, PaymentProvider


class AppointmentType(UUIDModel, TimeStampedModel):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True, db_index=True)

    base_hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))])
    currency = models.CharField(max_length=3, default="USD")

    allowed_durations_minutes = models.CharField(
        max_length=60,
        default="30,60,90",
        help_text="CSV durations, e.g. 30,60,90"
    )

    pricing_rules_json = models.TextField(
        blank=True,
        default="",
        help_text="JSON rules for dynamic pricing (urgency/weekend/complexity).",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class AvailabilityRule(UUIDModel, TimeStampedModel):
    weekday = models.CharField(max_length=5, choices=WeekdayChoices.choices, db_index=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["weekday", "start_time"]

    def __str__(self) -> str:
        return f"{self.weekday} {self.start_time}-{self.end_time}"


class AppointmentSlot(UUIDModel, TimeStampedModel):
    start_at = models.DateTimeField(db_index=True)
    end_at = models.DateTimeField(db_index=True)

    is_booked = models.BooleanField(default=False, db_index=True)
    booked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["start_at"]
        indexes = [
            models.Index(fields=["start_at", "is_booked"]),
        ]

    def __str__(self) -> str:
        return f"{self.start_at} -> {self.end_at}"


class Appointment(UUIDModel, TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="appointments")
    slot = models.OneToOneField(AppointmentSlot, on_delete=models.PROTECT, related_name="appointment")
    appointment_type = models.ForeignKey(AppointmentType, on_delete=models.PROTECT, related_name="appointments")

    status = models.CharField(max_length=20, choices=AppointmentStatus.choices, default=AppointmentStatus.PENDING, db_index=True)

    duration_minutes = models.PositiveIntegerField(default=60)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))])
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))])
    currency = models.CharField(max_length=3, default="USD")

    provider = models.CharField(max_length=20, choices=PaymentProvider.choices, default=PaymentProvider.STRIPE)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING, db_index=True)
    provider_payment_id = models.CharField(max_length=160, blank=True, default="")

    meeting_link = models.URLField(blank=True, default="")
    notes = models.TextField(blank=True, default="")

    confirmed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "status", "payment_status"])]

    def confirm(self) -> None:
        self.status = AppointmentStatus.CONFIRMED
        self.confirmed_at = timezone.now()
        self.save(update_fields=["status", "confirmed_at"])

    def __str__(self) -> str:
        return f"{self.user_id} - {self.appointment_type.name} ({self.status})"
