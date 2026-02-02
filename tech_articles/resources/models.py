from __future__ import annotations

from django.db import models
from django.conf import settings
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
        blank=True,
        default="",
        help_text=_("S3 key/path to the document file (legacy)"),
    )
    
    media_file = models.ForeignKey(
        "MediaFile",
        verbose_name=_("media file"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="resource_documents",
        help_text=_("Linked media file from library"),
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


class MediaFolder(UUIDModel, TimeStampedModel):
    """Folder for organizing media files."""
    
    name = models.CharField(
        _("name"),
        max_length=255,
        help_text=_("Folder name"),
    )
    slug = models.SlugField(
        _("slug"),
        max_length=255,
        db_index=True,
        help_text=_("URL-friendly identifier"),
    )
    parent = models.ForeignKey(
        "self",
        verbose_name=_("parent folder"),
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="subfolders",
        help_text=_("Parent folder for nested structure"),
    )
    description = models.TextField(
        _("description"),
        blank=True,
        default="",
        help_text=_("Folder description"),
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("created by"),
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_folders",
        help_text=_("User who created this folder"),
    )
    
    class Meta:
        verbose_name = _("media folder")
        verbose_name_plural = _("media folders")
        ordering = ["name"]
        unique_together = [("parent", "slug")]
        indexes = [
            models.Index(fields=["parent", "name"]),
        ]
    
    def __str__(self) -> str:
        return self.name
    
    def get_full_path(self) -> str:
        """Get the full path of the folder including parent folders."""
        if self.parent:
            return f"{self.parent.get_full_path()}/{self.name}"
        return self.name


class MediaTag(UUIDModel, TimeStampedModel):
    """Tag for categorizing media files."""
    
    name = models.CharField(
        _("name"),
        max_length=100,
        unique=True,
        help_text=_("Tag name"),
    )
    slug = models.SlugField(
        _("slug"),
        max_length=120,
        unique=True,
        db_index=True,
        help_text=_("URL-friendly identifier"),
    )
    
    class Meta:
        verbose_name = _("media tag")
        verbose_name_plural = _("media tags")
        ordering = ["name"]
    
    def __str__(self) -> str:
        return self.name


class MediaFile(UUIDModel, TimeStampedModel):
    """Media file with metadata and storage information."""
    
    FILE_TYPE_CHOICES = [
        ("image", _("Image")),
        ("video", _("Video")),
        ("document", _("Document")),
        ("audio", _("Audio")),
        ("other", _("Other")),
    ]
    
    title = models.CharField(
        _("title"),
        max_length=255,
        help_text=_("Media file title"),
    )
    description = models.TextField(
        _("description"),
        blank=True,
        default="",
        help_text=_("Detailed description of the media"),
    )
    alt_text = models.CharField(
        _("alt text"),
        max_length=255,
        blank=True,
        default="",
        help_text=_("Alternative text for accessibility"),
    )
    
    file_key = models.CharField(
        _("file key"),
        max_length=512,
        db_index=True,
        unique=True,
        help_text=_("S3 key/path to the file"),
    )
    file_name = models.CharField(
        _("file name"),
        max_length=255,
        help_text=_("Original file name"),
    )
    file_type = models.CharField(
        _("file type"),
        max_length=20,
        choices=FILE_TYPE_CHOICES,
        db_index=True,
        help_text=_("Type of file"),
    )
    mime_type = models.CharField(
        _("MIME type"),
        max_length=100,
        help_text=_("MIME type of the file"),
    )
    file_size = models.PositiveBigIntegerField(
        _("file size"),
        help_text=_("File size in bytes"),
    )
    
    # Image-specific fields
    width = models.PositiveIntegerField(
        _("width"),
        null=True,
        blank=True,
        help_text=_("Image width in pixels"),
    )
    height = models.PositiveIntegerField(
        _("height"),
        null=True,
        blank=True,
        help_text=_("Image height in pixels"),
    )
    
    # Optimized versions
    thumbnail_key = models.CharField(
        _("thumbnail key"),
        max_length=512,
        blank=True,
        default="",
        help_text=_("S3 key for thumbnail version"),
    )
    optimized_key = models.CharField(
        _("optimized key"),
        max_length=512,
        blank=True,
        default="",
        help_text=_("S3 key for optimized version"),
    )
    
    # Organization
    folder = models.ForeignKey(
        MediaFolder,
        verbose_name=_("folder"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="files",
        help_text=_("Folder containing this file"),
    )
    tags = models.ManyToManyField(
        MediaTag,
        verbose_name=_("tags"),
        related_name="files",
        blank=True,
        help_text=_("Tags for categorization"),
    )
    
    # Ownership and access
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("uploaded by"),
        on_delete=models.SET_NULL,
        null=True,
        related_name="uploaded_media",
        help_text=_("User who uploaded this file"),
    )
    access_level = models.CharField(
        _("access level"),
        max_length=30,
        choices=ResourceAccessLevel.choices,
        default=ResourceAccessLevel.FREE,
        db_index=True,
        help_text=_("Access level required to view this file"),
    )
    
    # Stats
    download_count = models.PositiveIntegerField(
        _("download count"),
        default=0,
        help_text=_("Number of times file has been downloaded"),
    )
    
    class Meta:
        verbose_name = _("media file")
        verbose_name_plural = _("media files")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["file_type", "created_at"]),
            models.Index(fields=["folder", "file_type"]),
            models.Index(fields=["uploaded_by", "created_at"]),
        ]
    
    def __str__(self) -> str:
        return self.title or self.file_name
    
    @property
    def is_image(self) -> bool:
        """Check if file is an image."""
        return self.file_type == "image"
    
    @property
    def is_video(self) -> bool:
        """Check if file is a video."""
        return self.file_type == "video"
    
    @property
    def is_document(self) -> bool:
        """Check if file is a document."""
        return self.file_type == "document"
    
    @property
    def file_size_mb(self) -> float:
        """Get file size in megabytes."""
        return round(self.file_size / (1024 * 1024), 2)
    
    def get_file_url(self) -> str:
        """Get public URL for the file."""
        from .storage import MediaStorage
        return MediaStorage.get_file_url(self.file_key)
    
    def get_thumbnail_url(self) -> str | None:
        """Get public URL for thumbnail."""
        if self.thumbnail_key:
            from .storage import MediaStorage
            return MediaStorage.get_file_url(self.thumbnail_key)
        return None
    
    def get_optimized_url(self) -> str | None:
        """Get public URL for optimized version."""
        if self.optimized_key:
            from .storage import MediaStorage
            return MediaStorage.get_file_url(self.optimized_key)
        return None
