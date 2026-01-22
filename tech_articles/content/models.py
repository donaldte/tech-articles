from __future__ import annotations

from decimal import Decimal
from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from django.conf import settings

from tech_articles.common.models import UUIDModel, TimeStampedModel, PublishableModel
from tech_articles.utils.enums import LanguageChoices, DifficultyChoices, ArticleAccessType, ArticleStatus


class Category(UUIDModel, TimeStampedModel):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, db_index=True)
    description = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True, db_index=True)
    sort_order = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ["sort_order", "name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:140]
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Tag(UUIDModel, TimeStampedModel):
    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=80, unique=True, db_index=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:80]
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Article(UUIDModel, TimeStampedModel, PublishableModel):
    # Core
    title = models.CharField(max_length=240)
    slug = models.SlugField(max_length=260, unique=True, db_index=True)
    language = models.CharField(max_length=5, choices=LanguageChoices.choices, db_index=True)
    status = models.CharField(max_length=20, choices=ArticleStatus.choices, default=ArticleStatus.DRAFT, db_index=True)
    difficulty = models.CharField(max_length=20, choices=DifficultyChoices.choices, default=DifficultyChoices.BEGINNER, db_index=True)

    # Monetization
    access_type = models.CharField(max_length=10, choices=ArticleAccessType.choices, default=ArticleAccessType.FREE, db_index=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(Decimal("0.00"))])
    currency = models.CharField(max_length=3, default="USD")

    # SEO
    seo_title = models.CharField(max_length=70, blank=True, default="")
    seo_description = models.CharField(max_length=160, blank=True, default="")
    canonical_url = models.URLField(blank=True, default="")

    # Content
    summary = models.TextField(blank=True, default="")
    cover_image_key = models.CharField(
        max_length=512,
        blank=True,
        default="",
        help_text="S3 key/path for cover image (optimized)."
    )
    cover_alt_text = models.CharField(max_length=180, blank=True, default="")
    reading_time_minutes = models.PositiveIntegerField(default=0)

    # YouTube preview
    youtube_url = models.URLField(blank=True, default="")
    youtube_start_seconds = models.PositiveIntegerField(default=0)

    # Relations
    categories = models.ManyToManyField(Category, related_name="articles", blank=True)
    tags = models.ManyToManyField(Tag, related_name="articles", blank=True)

    # Authoring
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="authored_articles",
    )

    class Meta:
        ordering = ["-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["language", "status", "access_type"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:260]
        # enforce: paid article should have price
        if self.access_type == ArticleAccessType.PAID and self.price is None:
            self.price = Decimal("0.00")
        super().save(*args, **kwargs)

    @property
    def is_published(self) -> bool:
        return self.status == ArticleStatus.PUBLISHED

    def __str__(self) -> str:
        return self.title


class ArticlePage(UUIDModel, TimeStampedModel):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="pages")
    page_number = models.PositiveIntegerField(db_index=True)
    title = models.CharField(max_length=240, blank=True, default="")
    slug = models.SlugField(max_length=260, db_index=True, blank=True, default="")

    # Markdown / MDX raw content
    content = models.TextField()

    # Table of contents precomputed (json as text, to avoid Postgres JSON dependency early)
    toc_json = models.TextField(blank=True, default="")

    # Optional: store preview cut for paywall
    preview_content = models.TextField(blank=True, default="")

    class Meta:
        unique_together = [("article", "page_number")]
        ordering = ["article", "page_number"]

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            self.slug = slugify(self.title)[:260]
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.article.title} — Page {self.page_number}"
