from __future__ import annotations

import secrets
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from tech_articles.common.models import UUIDModel, TimeStampedModel
from tech_articles.utils.enums import LanguageChoices, ScheduleMode, EmailStatus


class NewsletterSubscriber(UUIDModel, TimeStampedModel):
    email = models.EmailField(
        _("email address"),
        unique=True,
        db_index=True,
        help_text=_("Subscriber email address"),
    )
    language = models.CharField(
        _("language"),
        max_length=5,
        choices=LanguageChoices.choices,
        default=LanguageChoices.FR,
        db_index=True,
        help_text=_("Preferred language for newsletters"),
    )

    is_active = models.BooleanField(
        _("is active"),
        default=True,
        db_index=True,
        help_text=_("Whether the subscription is active"),
    )
    is_confirmed = models.BooleanField(
        _("is confirmed"),
        default=False,
        db_index=True,
        help_text=_("Whether the email has been confirmed"),
    )
    confirmed_at = models.DateTimeField(
        _("confirmed at"),
        null=True,
        blank=True,
        help_text=_("Date and time of email confirmation"),
    )

    unsub_token = models.CharField(
        _("unsubscribe token"),
        max_length=64,
        unique=True,
        editable=False,
        db_index=True,
        help_text=_("Token for unsubscribing without login"),
    )

    tags = models.CharField(
        _("tags"),
        max_length=500,
        blank=True,
        default="",
        help_text=_("Comma-separated tags for segmentation"),
    )

    consent_given_at = models.DateTimeField(
        _("consent given at"),
        null=True,
        blank=True,
        help_text=_("GDPR: Date and time when user gave consent"),
    )

    ip_address = models.GenericIPAddressField(
        _("IP address"),
        null=True,
        blank=True,
        help_text=_("IP address when subscriber signed up"),
    )

    last_email_sent_at = models.DateTimeField(
        _("last email sent at"),
        null=True,
        blank=True,
        help_text=_("Date and time of the last email sent"),
    )

    email_open_count = models.PositiveIntegerField(
        _("email open count"),
        default=0,
        help_text=_("Number of emails opened by subscriber"),
    )

    email_click_count = models.PositiveIntegerField(
        _("email click count"),
        default=0,
        help_text=_("Number of links clicked in emails"),
    )

    class Meta:
        verbose_name = _("newsletter subscriber")
        verbose_name_plural = _("newsletter subscribers")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_active", "is_confirmed"]),
        ]

    def save(self, *args, **kwargs):
        if not self.unsub_token:
            self.unsub_token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)

    def confirm(self) -> None:
        self.is_confirmed = True
        self.confirmed_at = timezone.now()
        self.save(update_fields=["is_confirmed", "confirmed_at"])

    def unsubscribe(self) -> None:
        """Mark subscriber as inactive."""
        self.is_active = False
        self.save(update_fields=["is_active"])

    def get_tags_list(self) -> list[str]:
        """Return tags as a list."""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(",") if tag.strip()]

    def __str__(self) -> str:
        return self.email


class NewsletterCampaign(UUIDModel, TimeStampedModel):
    name = models.CharField(
        _("name"),
        max_length=120,
        help_text=_("Campaign name"),
    )
    schedule_mode = models.CharField(
        _("schedule mode"),
        max_length=30,
        choices=ScheduleMode.choices,
        default=ScheduleMode.DAILY_5AM,
        help_text=_("Frequency and time for sending newsletters"),
    )
    is_active = models.BooleanField(
        _("is active"),
        default=True,
        db_index=True,
        help_text=_("Whether the campaign is active"),
    )

    template_subject = models.CharField(
        _("template subject"),
        max_length=160,
        default="Article du jour",
        help_text=_("Email subject template"),
    )
    template_body = models.TextField(
        _("template body"),
        default="",
        help_text=_("Email body template (HTML)"),
    )

    last_run_at = models.DateTimeField(
        _("last run at"),
        null=True,
        blank=True,
        help_text=_("Last execution time of the campaign"),
    )

    class Meta:
        verbose_name = _("newsletter campaign")
        verbose_name_plural = _("newsletter campaigns")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name


class EmailLog(UUIDModel, TimeStampedModel):
    to_email = models.EmailField(
        _("recipient email"),
        db_index=True,
        help_text=_("Email address of the recipient"),
    )
    subject = models.CharField(
        _("subject"),
        max_length=200,
        help_text=_("Email subject line"),
    )
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=EmailStatus.choices,
        default=EmailStatus.QUEUED,
        db_index=True,
        help_text=_("Current status of the email"),
    )

    provider = models.CharField(
        _("provider"),
        max_length=30,
        default="ses",
        help_text=_("Email service provider (SES, SendGrid, etc.)"),
    )
    provider_message_id = models.CharField(
        _("provider message ID"),
        max_length=180,
        blank=True,
        default="",
        help_text=_("Message ID from the provider"),
    )

    error_message = models.TextField(
        _("error message"),
        blank=True,
        default="",
        help_text=_("Error details if sending failed"),
    )
    sent_at = models.DateTimeField(
        _("sent at"),
        null=True,
        blank=True,
        help_text=_("Time when the email was sent"),
    )

    class Meta:
        verbose_name = _("email log")
        verbose_name_plural = _("email logs")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["to_email", "status"]),
            models.Index(fields=["status", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.to_email} - {self.status}"
