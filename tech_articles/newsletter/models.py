from __future__ import annotations

import secrets
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from tech_articles.common.models import UUIDModel, TimeStampedModel
from tech_articles.utils.enums import LanguageChoices, ScheduleMode, EmailStatus, SubscriberStatus


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
    
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=SubscriberStatus.choices,
        default=SubscriberStatus.ACTIVE,
        db_index=True,
        help_text=_("Current subscriber status"),
    )

    unsub_token = models.CharField(
        _("unsubscribe token"),
        max_length=64,
        unique=True,
        editable=False,
        db_index=True,
        help_text=_("Token for unsubscribing without login"),
    )
    
    confirm_token = models.CharField(
        _("confirmation token"),
        max_length=64,
        unique=True,
        editable=False,
        db_index=True,
        null=True,
        blank=True,
        help_text=_("Token for email confirmation (double opt-in)"),
    )
    
    consent_given_at = models.DateTimeField(
        _("consent given at"),
        null=True,
        blank=True,
        help_text=_("Date and time when GDPR consent was given"),
    )
    
    ip_address = models.GenericIPAddressField(
        _("IP address"),
        null=True,
        blank=True,
        help_text=_("IP address used during subscription"),
    )

    class Meta:
        verbose_name = _("newsletter subscriber")
        verbose_name_plural = _("newsletter subscribers")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_active", "is_confirmed"]),
            models.Index(fields=["status", "is_confirmed"]),
        ]

    def save(self, *args, **kwargs):
        if not self.unsub_token:
            self.unsub_token = secrets.token_urlsafe(32)
        if not self.confirm_token:
            self.confirm_token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)

    def confirm(self) -> None:
        self.is_confirmed = True
        self.confirmed_at = timezone.now()
        self.status = SubscriberStatus.ACTIVE
        self.save(update_fields=["is_confirmed", "confirmed_at", "status"])
    
    def unsubscribe(self) -> None:
        self.is_active = False
        self.status = SubscriberStatus.UNSUBSCRIBED
        self.save(update_fields=["is_active", "status"])

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


class SubscriberTag(UUIDModel, TimeStampedModel):
    """Tags for categorizing newsletter subscribers."""
    name = models.CharField(
        _("name"),
        max_length=50,
        unique=True,
        help_text=_("Tag name"),
    )
    description = models.TextField(
        _("description"),
        blank=True,
        default="",
        help_text=_("Tag description"),
    )
    color = models.CharField(
        _("color"),
        max_length=7,
        default="#3B82F6",
        help_text=_("Tag color in hex format"),
    )

    class Meta:
        verbose_name = _("subscriber tag")
        verbose_name_plural = _("subscriber tags")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class SubscriberSegment(UUIDModel, TimeStampedModel):
    """Segments for grouping subscribers by criteria."""
    name = models.CharField(
        _("name"),
        max_length=100,
        unique=True,
        help_text=_("Segment name"),
    )
    description = models.TextField(
        _("description"),
        blank=True,
        default="",
        help_text=_("Segment description"),
    )
    subscribers = models.ManyToManyField(
        NewsletterSubscriber,
        related_name="segments",
        blank=True,
        verbose_name=_("subscribers"),
    )
    tags = models.ManyToManyField(
        SubscriberTag,
        related_name="segments",
        blank=True,
        verbose_name=_("tags"),
    )

    class Meta:
        verbose_name = _("subscriber segment")
        verbose_name_plural = _("subscriber segments")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class SubscriberEngagement(UUIDModel, TimeStampedModel):
    """Track engagement history for subscribers."""
    subscriber = models.ForeignKey(
        NewsletterSubscriber,
        on_delete=models.CASCADE,
        related_name="engagements",
        verbose_name=_("subscriber"),
    )
    email_log = models.ForeignKey(
        EmailLog,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="engagements",
        verbose_name=_("email log"),
    )
    action = models.CharField(
        _("action"),
        max_length=30,
        help_text=_("Engagement action (opened, clicked, etc.)"),
    )
    metadata = models.JSONField(
        _("metadata"),
        default=dict,
        blank=True,
        help_text=_("Additional engagement data"),
    )

    class Meta:
        verbose_name = _("subscriber engagement")
        verbose_name_plural = _("subscriber engagements")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["subscriber", "action"]),
            models.Index(fields=["action", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.subscriber.email} - {self.action}"


class SubscriberTagAssignment(UUIDModel, TimeStampedModel):
    """Association between subscribers and tags."""
    subscriber = models.ForeignKey(
        NewsletterSubscriber,
        on_delete=models.CASCADE,
        related_name="tag_assignments",
        verbose_name=_("subscriber"),
    )
    tag = models.ForeignKey(
        SubscriberTag,
        on_delete=models.CASCADE,
        related_name="assignments",
        verbose_name=_("tag"),
    )

    class Meta:
        verbose_name = _("subscriber tag assignment")
        verbose_name_plural = _("subscriber tag assignments")
        unique_together = [["subscriber", "tag"]]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.subscriber.email} - {self.tag.name}"

