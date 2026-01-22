from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from tech_articles.common.models import UUIDModel, TimeStampedModel
from tech_articles.utils.enums import EventType


class Event(UUIDModel, TimeStampedModel):
    event_type = models.CharField(
        _("event type"),
        max_length=40,
        choices=EventType.choices,
        db_index=True,
        help_text=_("Type of event"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("user"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="events",
        help_text=_("Associated user (if authenticated)"),
    )
    anonymous_id = models.CharField(
        _("anonymous ID"),
        max_length=120,
        blank=True,
        default="",
        db_index=True,
        help_text=_("Anonymous visitor ID"),
    )

    path = models.CharField(
        _("path"),
        max_length=512,
        blank=True,
        default="",
        help_text=_("URL path where event occurred"),
    )
    referrer = models.CharField(
        _("referrer"),
        max_length=512,
        blank=True,
        default="",
        help_text=_("HTTP referrer URL"),
    )
    user_agent = models.CharField(
        _("user agent"),
        max_length=512,
        blank=True,
        default="",
        help_text=_("Browser user agent string"),
    )
    ip_hash = models.CharField(
        _("IP hash"),
        max_length=128,
        blank=True,
        default="",
        help_text=_("Hashed IP address for privacy"),
    )

    metadata_json = models.TextField(
        _("metadata"),
        blank=True,
        default="",
        help_text=_("Additional event data in JSON format"),
    )

    class Meta:
        verbose_name = _("event")
        verbose_name_plural = _("events")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["event_type", "created_at"]),
            models.Index(fields=["user", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.event_type} - {self.created_at}"
