from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from urllib.parse import urlparse, unquote_plus

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

    file_name = models.CharField(
        _("file name"),
        max_length=255,
        help_text=_("Original file name"),
    )

    file_size = models.BigIntegerField(
        _("file size"),
        default=0,
        help_text=_("File size in bytes"),
    )

    content_type = models.CharField(
        _("content type"),
        max_length=100,
        blank=True,
        default="",
        help_text=_("MIME type of the file"),
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
        verbose_name=_("article"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="resources",
        help_text=_("Associated article"),
    )
    category = models.ForeignKey(
        Category,
        verbose_name=_("category"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="resources",
        help_text=_("Associated category"),
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("uploaded by"),
        on_delete=models.SET_NULL,
        null=True,
        related_name="uploaded_resources",
        help_text=_("User who uploaded the resource"),
    )

    watermark_enabled = models.BooleanField(
        _("watermark enabled"),
        default=True,
        help_text=_("Enable watermark on document"),
    )

    download_count = models.PositiveIntegerField(
        _("download count"),
        default=0,
        help_text=_("Number of times downloaded"),
    )

    is_active = models.BooleanField(
        _("is active"),
        default=True,
        db_index=True,
        help_text=_("Whether the resource is available"),
    )

    class Meta:
        verbose_name = _("resource document")
        verbose_name_plural = _("resource documents")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["access_level", "created_at"]),
            models.Index(fields=["article", "is_active"]),
            models.Index(fields=["category", "is_active"]),
        ]

    def __str__(self) -> str:
        return self.title

    def get_file_extension(self) -> str:
        """Extract file extension from file name"""
        return self.file_name.rsplit('.', 1)[-1].lower() if '.' in self.file_name else ''

    def get_file_size_display(self) -> str:
        """Human-readable file size"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    def get_file_name_from_key(self) -> str:
        """Extract filename from S3 key"""
        if self.file_key:
            try:
                decoded_url = unquote_plus(self.file_key)
                return decoded_url.split('/')[-1]
            except Exception:
                return self.file_name
        return self.file_name

    def get_signed_download_url(self, expires_in: int = 300):
        """
        Generate temporary signed URL for downloading the resource

        Args:
            expires_in: URL validity in seconds (default 5 minutes)

        Returns:
            Presigned URL or None
        """
        if not self.file_key:
            return None

        from tech_articles.resources.utils.s3_manager import s3_resource_manager
        return s3_resource_manager.generate_signed_download_url(
            self.file_key,
            expires_in=expires_in
        )

    def increment_download_count(self):
        """Safely increment download counter"""
        self.download_count += 1
        self.save(update_fields=['download_count'])



