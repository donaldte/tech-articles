from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from tech_articles.common.models import UUIDModel, TimeStampedModel
from tech_articles.content.models import Article, Category
from tech_articles.utils.enums import ResourceAccessLevel


class ResourceDocument(UUIDModel, TimeStampedModel):
    title = models.CharField(
        _("title"),
        max_length=240,
        help_text=_("Title of the resource document"),
    )
    description = models.TextField(
        _("description"),
        blank=True,
        default="",
        help_text=_("Detailed description of the resource"),
    )

    file_key = models.CharField(
        _("file key"),
        max_length=512,
        db_index=True,
        help_text=_("S3 key/path to the document file"),
    )

    access_level = models.CharField(
        _("access level"),
        max_length=30,
        choices=ResourceAccessLevel.choices,
        default=ResourceAccessLevel.PREMIUM,
        db_index=True,
        help_text=_("Access level required to view this resource"),
    )

    article = models.ForeignKey(
        Article,
        _("article"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="resources",
        help_text=_("Associated article"),
    )
    category = models.ForeignKey(
        Category,
        _("category"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="resources",
        help_text=_("Associated category"),
    )

    watermark_enabled = models.BooleanField(
        _("watermark enabled"),
        default=True,
        help_text=_("Enable watermark on document"),
    )

    class Meta:
        verbose_name = _("resource document")
        verbose_name_plural = _("resource documents")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["access_level", "created_at"]),
        ]

    def __str__(self) -> str:
        return self.title
