from __future__ import annotations

import uuid
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """Base: created_at / updated_at."""
    created_at = models.DateTimeField(default=timezone.now, editable=False, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True


class UUIDModel(models.Model):
    """Base: UUID primary key."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class PublishableModel(models.Model):
    """Optional base for published_at."""
    published_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """Optional soft delete."""
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        abstract = True

    def soft_delete(self) -> None:
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])
