from __future__ import annotations

from django.db import models
from tech_articles.common.models import UUIDModel, TimeStampedModel
from tech_articles.content.models import Article, Category
from tech_articles.utils.enums import ResourceAccessLevel


class ResourceDocument(UUIDModel, TimeStampedModel):
    title = models.CharField(max_length=240)
    description = models.TextField(blank=True, default="")

    # S3 key/path
    file_key = models.CharField(max_length=512, db_index=True)

    access_level = models.CharField(max_length=30, choices=ResourceAccessLevel.choices, default=ResourceAccessLevel.PREMIUM, db_index=True)

    # Optional relations
    article = models.ForeignKey(Article, null=True, blank=True, on_delete=models.SET_NULL, related_name="resources")
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL, related_name="resources")

    # Optional watermark settings
    watermark_enabled = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title
