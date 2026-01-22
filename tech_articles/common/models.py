from __future__ import annotations

import uuid
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    """
    Base model that automatically tracks creation and modification timestamps.
    Provides created_at and updated_at fields.
    """
    created_at = models.DateTimeField(
        _("created at"),
        default=timezone.now,
        editable=False,
        db_index=True,
        help_text=_("Date and time when the record was created"),
    )
    updated_at = models.DateTimeField(
        _("updated at"),
        auto_now=True,
        db_index=True,
        help_text=_("Date and time when the record was last updated"),
    )

    class Meta:
        abstract = True


class UUIDModel(models.Model):
    """
    Base model that uses UUID as primary key instead of auto-incrementing integer.
    Provides better privacy and distributed system compatibility.
    """
    id = models.UUIDField(
        _("ID"),
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_("Unique identifier"),
    )

    class Meta:
        abstract = True


class PublishableModel(models.Model):
    """
    Base model for content that can be published at a specific date/time.
    Provides published_at field for managing publication scheduling.
    """
    published_at = models.DateTimeField(
        _("published at"),
        null=True,
        blank=True,
        db_index=True,
        help_text=_("Date and time when the content was published"),
    )

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """
    Base model that implements soft delete functionality.
    Records are marked as deleted instead of being permanently removed from database.
    """
    deleted_at = models.DateTimeField(
        _("deleted at"),
        null=True,
        blank=True,
        db_index=True,
        help_text=_("Date and time when the record was soft deleted"),
    )

    class Meta:
        abstract = True

    def soft_delete(self) -> None:
        """
        Perform a soft delete by setting deleted_at timestamp.

        Returns:
            None

        """
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])
