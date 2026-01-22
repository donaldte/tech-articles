from __future__ import annotations

from decimal import Decimal
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from tech_articles.common.models import UUIDModel, TimeStampedModel
from tech_articles.utils.enums import WeekdayChoices, AppointmentStatus, PaymentStatus, PaymentProvider


class AppointmentType(UUIDModel, TimeStampedModel):
    name = models.CharField(
        _("name"),
        max_length=120,
        unique=True,
        help_text=_("Appointment type name"),
    )
    description = models.TextField(
        _("description"),
        blank=True,
        default="",
        help_text=_("Detailed description"),
    )
    is_active = models.BooleanField(
        _("is active"),
        default=True,
        db_index=True,
        help_text=_("Whether this type is available for booking"),
    )

    base_hourly_rate = models.DecimalField(
        _("base hourly rate"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text=_("Base hourly rate for this appointment type"),
    )
    currency = models.CharField(
        _("currency"),
        max_length=3,
        default="USD",
        help_text=_("Currency code (ISO 4217)"),
    )

    allowed_durations_minutes = models.CharField(
        _("allowed durations (minutes)"),
        max_length=60,
        default="30,60,90",
        help_text=_("Comma-separated list of allowed durations"),
    )

    pricing_rules_json = models.TextField(
        _("pricing rules"),
        blank=True,
        default="",
        help_text=_("JSON rules for dynamic pricing (urgency/weekend/complexity)"),
    )

    class Meta:
        verbose_name = _("appointment type")
        verbose_name_plural = _("appointment types")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class AvailabilityRule(UUIDModel, TimeStampedModel):
    weekday = models.CharField(
        _("weekday"),
        max_length=5,
        choices=WeekdayChoices.choices,
        db_index=True,
        help_text=_("Day of week"),
    )
    start_time = models.TimeField(
        _("start time"),
        help_text=_("Availability start time"),
    )
    end_time = models.TimeField(
        _("end time"),
        help_text=_("Availability end time"),
    )
    is_active = models.BooleanField(
        _("is active"),
        default=True,
        db_index=True,
        help_text=_("Whether this rule is active"),
    )

    class Meta:
        verbose_name = _("availability rule")
        verbose_name_plural = _("availability rules")
        ordering = ["weekday", "start_time"]

    def __str__(self) -> str:
        return f"{self.weekday} {self.start_time}-{self.end_time}"


class AppointmentSlot(UUIDModel, TimeStampedModel):
    start_at = models.DateTimeField(
        _("start time"),
        db_index=True,
        help_text=_("Appointment start date and time"),
    )
    end_at = models.DateTimeField(
        _("end time"),
        db_index=True,
        help_text=_("Appointment end date and time"),
    )

    is_booked = models.BooleanField(
        _("is booked"),
        default=False,
        db_index=True,
        help_text=_("Whether the slot has been booked"),
    )
    booked_at = models.DateTimeField(
        _("booked at"),
        null=True,
        blank=True,
        help_text=_("Date and time when the slot was booked"),
    )

    class Meta:
        verbose_name = _("appointment slot")
        verbose_name_plural = _("appointment slots")
        ordering = ["start_at"]
        indexes = [
            models.Index(fields=["start_at", "is_booked"]),
        ]

    def __str__(self) -> str:
        return f"{self.start_at} -> {self.end_at}"


class Appointment(UUIDModel, TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("user"),
        on_delete=models.CASCADE,
        related_name="appointments",
        help_text=_("Appointment user"),
    )
    slot = models.OneToOneField(
        AppointmentSlot,
        verbose_name=_("slot"),
        on_delete=models.PROTECT,
        related_name="appointment",
        help_text=_("Associated time slot"),
    )
    appointment_type = models.ForeignKey(
        AppointmentType,
        verbose_name=_("type"),
        on_delete=models.PROTECT,
        related_name="appointments",
        help_text=_("Appointment type"),
    )

    status = models.CharField(
        _("status"),
        max_length=20,
        choices=AppointmentStatus.choices,
        default=AppointmentStatus.PENDING,
        db_index=True,
        help_text=_("Appointment status"),
    )

    duration_minutes = models.PositiveIntegerField(
        _("duration (minutes)"),
        default=60,
        help_text=_("Appointment duration in minutes"),
    )
    hourly_rate = models.DecimalField(
        _("hourly rate"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text=_("Applied hourly rate"),
    )
    total_amount = models.DecimalField(
        _("total amount"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text=_("Total appointment cost"),
    )
    currency = models.CharField(
        _("currency"),
        max_length=3,
        default="USD",
        help_text=_("Currency code (ISO 4217)"),
    )

    provider = models.CharField(
        _("payment provider"),
        max_length=20,
        choices=PaymentProvider.choices,
        default=PaymentProvider.STRIPE,
        help_text=_("Payment service provider"),
    )
    payment_status = models.CharField(
        _("payment status"),
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        db_index=True,
        help_text=_("Payment status"),
    )
    provider_payment_id = models.CharField(
        _("provider payment ID"),
        max_length=160,
        blank=True,
        default="",
        help_text=_("External payment ID"),
    )

    meeting_link = models.URLField(
        _("meeting link"),
        blank=True,
        default="",
        help_text=_("Video conference or meeting URL"),
    )
    notes = models.TextField(
        _("notes"),
        blank=True,
        default="",
        help_text=_("Additional notes or instructions"),
    )

    confirmed_at = models.DateTimeField(
        _("confirmed at"),
        null=True,
        blank=True,
        help_text=_("Appointment confirmation date/time"),
    )
    cancelled_at = models.DateTimeField(
        _("cancelled at"),
        null=True,
        blank=True,
        help_text=_("Appointment cancellation date/time"),
    )

    class Meta:
        verbose_name = _("appointment")
        verbose_name_plural = _("appointments")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status", "payment_status"]),
        ]

    def confirm(self) -> None:
        self.status = AppointmentStatus.CONFIRMED
        self.confirmed_at = timezone.now()
        self.save(update_fields=["status", "confirmed_at"])

    def __str__(self) -> str:
        return f"{self.user_id} - {self.appointment_type.name} ({self.status})"
