from __future__ import annotations

import secrets
from django.db import models
from django.utils import timezone

from tech_articles.common.models import UUIDModel, TimeStampedModel
from tech_articles.utils.enums import LanguageChoices, ScheduleMode, EmailStatus


class NewsletterSubscriber(UUIDModel, TimeStampedModel):
    email = models.EmailField(unique=True, db_index=True)
    language = models.CharField(max_length=5, choices=LanguageChoices.choices, default=LanguageChoices.FR, db_index=True)

    is_active = models.BooleanField(default=True, db_index=True)
    is_confirmed = models.BooleanField(default=False, db_index=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    unsub_token = models.CharField(max_length=64, unique=True, editable=False, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.unsub_token:
            self.unsub_token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)

    def confirm(self) -> None:
        self.is_confirmed = True
        self.confirmed_at = timezone.now()
        self.save(update_fields=["is_confirmed", "confirmed_at"])

    def __str__(self) -> str:
        return self.email


class NewsletterCampaign(UUIDModel, TimeStampedModel):
    name = models.CharField(max_length=120)
    schedule_mode = models.CharField(max_length=30, choices=ScheduleMode.choices, default=ScheduleMode.DAILY_5AM)
    is_active = models.BooleanField(default=True, db_index=True)

    template_subject = models.CharField(max_length=160, default="Article du jour")
    template_body = models.TextField(default="")

    last_run_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return self.name


class EmailLog(UUIDModel, TimeStampedModel):
    to_email = models.EmailField(db_index=True)
    subject = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=EmailStatus.choices, default=EmailStatus.QUEUED, db_index=True)

    provider = models.CharField(max_length=30, default="ses")
    provider_message_id = models.CharField(max_length=180, blank=True, default="")

    error_message = models.TextField(blank=True, default="")
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
