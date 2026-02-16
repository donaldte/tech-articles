from __future__ import annotations

from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from tech_articles.common.models import UUIDModel, TimeStampedModel, PublishableModel
from tech_articles.utils.enums import LanguageChoices, DifficultyChoices, ArticleAccessType, ArticleStatus
from tech_articles.utils.db_functions import DbFunctions


class Category(UUIDModel, TimeStampedModel):
    name = models.CharField(
        _("name"),
        max_length=120,
        unique=True,
        help_text=_("Category name"),
    )
    slug = models.SlugField(
        _("slug"),
        max_length=140,
        unique=True,
        db_index=True,
        help_text=_("URL-friendly identifier"),
    )
    description = models.TextField(
        _("description"),
        blank=True,
        default="",
        help_text=_("Category description"),
    )
    is_active = models.BooleanField(
        _("is active"),
        default=True,
        db_index=True,
        help_text=_("Whether the category is visible"),
    )
    sort_order = models.PositiveIntegerField(
        _("sort order"),
        default=0,
        db_index=True,
        help_text=_("Display order in listings"),
    )

    class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")
        ordering = ["sort_order", "name"]
        indexes = [
            models.Index(fields=["is_active", "sort_order"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = DbFunctions.generate_unique_slug(self, self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Tag(UUIDModel, TimeStampedModel):
    name = models.CharField(
        _("name"),
        max_length=60,
        unique=True,
        help_text=_("Tag name"),
    )
    slug = models.SlugField(
        _("slug"),
        max_length=80,
        unique=True,
        db_index=True,
        help_text=_("URL-friendly identifier"),
    )

    class Meta:
        verbose_name = _("tag")
        verbose_name_plural = _("tags")
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = DbFunctions.generate_unique_slug(self, self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Article(UUIDModel, TimeStampedModel, PublishableModel):
    title = models.CharField(
        _("title"),
        max_length=240,
        help_text=_("Article title"),
    )
    slug = models.SlugField(
        _("slug"),
        max_length=260,
        unique=True,
        db_index=True,
        help_text=_("URL-friendly identifier"),
    )
    language = models.CharField(
        _("language"),
        max_length=5,
        choices=LanguageChoices.choices,
        db_index=True,
        help_text=_("Article language"),
    )
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=ArticleStatus.choices,
        default=ArticleStatus.DRAFT,
        db_index=True,
        help_text=_("Publication status"),
    )
    difficulty = models.CharField(
        _("difficulty level"),
        max_length=20,
        choices=DifficultyChoices.choices,
        default=DifficultyChoices.BEGINNER,
        db_index=True,
        help_text=_("Content difficulty level"),
    )

    access_type = models.CharField(
        _("access type"),
        max_length=10,
        choices=ArticleAccessType.choices,
        default=ArticleAccessType.FREE,
        db_index=True,
        help_text=_("Free or paid access"),
    )
    price = models.DecimalField(
        _("price"),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text=_("Article price (if paid)"),
    )
    currency = models.CharField(
        _("currency"),
        max_length=3,
        default="USD",
        help_text=_("Currency code (ISO 4217)"),
    )

    seo_title = models.CharField(
        _("SEO title"),
        max_length=70,
        blank=True,
        default="",
        help_text=_("Meta title for search engines"),
    )
    seo_description = models.CharField(
        _("SEO description"),
        max_length=160,
        blank=True,
        default="",
        help_text=_("Meta description for search engines"),
    )
    canonical_url = models.URLField(
        _("canonical URL"),
        blank=True,
        default="",
        help_text=_("Canonical URL for duplicate content"),
    )

    summary = models.TextField(
        _("summary"),
        blank=True,
        default="",
        help_text=_("Brief article summary"),
    )
    cover_image_key = models.CharField(
        _("cover image key"),
        max_length=512,
        blank=True,
        default="",
        help_text=_("S3 key/path for cover image (optimized)"),
    )
    cover_alt_text = models.CharField(
        _("cover alt text"),
        max_length=180,
        blank=True,
        default="",
        help_text=_("Alternative text for cover image"),
    )
    reading_time_minutes = models.PositiveIntegerField(
        _("reading time (minutes)"),
        default=0,
        help_text=_("Estimated reading time in minutes"),
    )

    youtube_url = models.URLField(
        _("YouTube URL"),
        blank=True,
        default="",
        help_text=_("Optional YouTube video URL"),
    )
    youtube_start_seconds = models.PositiveIntegerField(
        _("YouTube start seconds"),
        default=0,
        help_text=_("Start time in seconds for video preview"),
    )

    categories = models.ManyToManyField(
        Category,
        verbose_name=_("categories"),
        related_name="articles",
        blank=True,
        help_text=_("Article categories"),
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name=_("tags"),
        related_name="articles",
        blank=True,
        help_text=_("Article tags"),
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("author"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="authored_articles",
        help_text=_("Article author"),
    )

    toc_json = models.TextField(
        _("table of contents"),
        blank=True,
        default="",
        help_text=_("Precomputed table of contents (JSON)"),
    )

    preview_content = models.TextField(
        _("preview content"),
        blank=True,
        default="",
        help_text=_("Content visible before paywall"),
    )

    class Meta:
        verbose_name = _("article")
        verbose_name_plural = _("articles")
        ordering = ["-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["language", "status", "access_type"]),
            models.Index(fields=["status", "published_at"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = DbFunctions.generate_unique_slug(self, self.title)
        if self.access_type == ArticleAccessType.PAID and self.price is None:
            self.price = Decimal("0.00")
        super().save(*args, **kwargs)

    @property
    def is_published(self) -> bool:
        return self.status == ArticleStatus.PUBLISHED

    def __str__(self) -> str:
        return self.title


class ArticlePage(UUIDModel, TimeStampedModel):
    article = models.ForeignKey(
        Article,
        verbose_name=_("article"),
        on_delete=models.CASCADE,
        related_name="pages",
        help_text=_("Parent article"),
    )
    page_number = models.PositiveIntegerField(
        _("page number"),
        db_index=True,
        help_text=_("Page sequence number"),
    )
    title = models.CharField(
        _("title"),
        max_length=240,
        blank=True,
        default="",
        help_text=_("Page section title"),
    )
    slug = models.SlugField(
        _("slug"),
        max_length=260,
        db_index=True,
        blank=True,
        default="",
        help_text=_("URL-friendly identifier"),
    )

    content = models.TextField(
        _("content"),
        help_text=_("Markdown/MDX formatted content"),
    )

    toc_json = models.TextField(
        _("table of contents"),
        blank=True,
        default="",
        help_text=_("Precomputed table of contents (JSON)"),
    )

    class Meta:
        verbose_name = _("article page")
        verbose_name_plural = _("article pages")
        unique_together = [("article", "page_number")]
        ordering = ["article", "page_number"]
        indexes = [
            models.Index(fields=["article", "page_number"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            # Generate unique slug relative to the parent article
            self.slug = DbFunctions.generate_unique_slug_for_related_object(
                self,
                self.title,
                related_field_name='article'
            )
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.article.title} — Page {self.page_number}"


class FeaturedArticles(UUIDModel, TimeStampedModel):
    """
    Configuration model for featured articles displayed on the home page.
    Allows selection of up to 3 articles to highlight.
    """
    first_feature = models.ForeignKey(
        Article,
        verbose_name=_("first featured article"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text=_("First article to feature on homepage"),
    )
    second_feature = models.ForeignKey(
        Article,
        verbose_name=_("second featured article"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text=_("Second article to feature on homepage"),
    )
    third_feature = models.ForeignKey(
        Article,
        verbose_name=_("third featured article"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text=_("Third article to feature on homepage"),
    )

    class Meta:
        verbose_name = _("featured articles")
        verbose_name_plural = _("featured articles")

    def __str__(self) -> str:
        return _("Featured Articles Configuration")
