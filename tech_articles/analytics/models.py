from __future__ import annotations

from django.db import models
from django.conf import settings
from tech_articles.common.models import UUIDModel, TimeStampedModel
from tech_articles.utils.enums import EventType


class Event(UUIDModel, TimeStampedModel):
    event_type = models.CharField(max_length=40, choices=EventType.choices, db_index=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="events")
    anonymous_id = models.CharField(max_length=120, blank=True, default="", db_index=True)

    path = models.CharField(max_length=512, blank=True, default="")
    referrer = models.CharField(max_length=512, blank=True, default="")
    user_agent = models.CharField(max_length=512, blank=True, default="")
    ip_hash = models.CharField(max_length=128, blank=True, default="")

    metadata_json = models.TextField(blank=True, default="")  # serialized json

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["event_type", "created_at"])]
