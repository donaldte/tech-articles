# Generated manually for subscription plan enhancements

import uuid
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("billing", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Add new fields to Plan model
        migrations.AddField(
            model_name="plan",
            name="description",
            field=models.TextField(
                blank=True,
                default="",
                help_text="Plan description",
                verbose_name="description",
            ),
        ),
        migrations.AddField(
            model_name="plan",
            name="is_popular",
            field=models.BooleanField(
                default=False,
                help_text="Mark this plan as popular/highlighted",
                verbose_name="is popular",
            ),
        ),
        migrations.AddField(
            model_name="plan",
            name="display_order",
            field=models.PositiveIntegerField(
                default=0,
                help_text="Order in which plans are displayed (lower numbers first)",
                verbose_name="display order",
            ),
        ),
        migrations.AddField(
            model_name="plan",
            name="custom_interval_count",
            field=models.PositiveIntegerField(
                blank=True,
                null=True,
                help_text="For custom intervals (e.g., every 3 months)",
                verbose_name="custom interval count",
            ),
        ),
        migrations.AddField(
            model_name="plan",
            name="trial_period_days",
            field=models.PositiveIntegerField(
                blank=True,
                null=True,
                help_text="Number of days for free trial",
                verbose_name="trial period (days)",
            ),
        ),
        migrations.AddField(
            model_name="plan",
            name="max_articles",
            field=models.PositiveIntegerField(
                blank=True,
                null=True,
                help_text="Maximum number of articles accessible (null = unlimited)",
                verbose_name="max articles",
            ),
        ),
        migrations.AddField(
            model_name="plan",
            name="max_resources",
            field=models.PositiveIntegerField(
                blank=True,
                null=True,
                help_text="Maximum number of resources accessible (null = unlimited)",
                verbose_name="max resources",
            ),
        ),
        migrations.AddField(
            model_name="plan",
            name="max_appointments",
            field=models.PositiveIntegerField(
                blank=True,
                null=True,
                help_text="Maximum number of appointments per month (null = unlimited)",
                verbose_name="max appointments",
            ),
        ),
        # Update Plan model ordering
        migrations.AlterModelOptions(
            name="plan",
            options={
                "ordering": ["display_order", "price"],
                "verbose_name": "plan",
                "verbose_name_plural": "plans",
            },
        ),
        # Update Plan model indexes
        migrations.AlterIndexTogether(
            name="plan",
            index_together=set(),
        ),
        migrations.AddIndex(
            model_name="plan",
            index=models.Index(
                fields=["is_active", "display_order"],
                name="billing_pla_is_acti_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="plan",
            index=models.Index(
                fields=["is_active", "price"],
                name="billing_pla_is_acti_price_idx",
            ),
        ),
        # Create PlanFeature model
        migrations.CreateModel(
            name="PlanFeature",
            fields=[
                (
                    "created_at",
                    models.DateTimeField(
                        db_index=True,
                        default=django.utils.timezone.now,
                        editable=False,
                        help_text="Date and time when the record was created",
                        verbose_name="created at",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True,
                        db_index=True,
                        help_text="Date and time when the record was last updated",
                        verbose_name="updated at",
                    ),
                ),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        help_text="Unique identifier",
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Name of the feature",
                        max_length=255,
                        verbose_name="feature name",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        default="",
                        help_text="Detailed description of the feature",
                        verbose_name="description",
                    ),
                ),
                (
                    "is_included",
                    models.BooleanField(
                        default=True,
                        help_text="Whether this feature is included or excluded",
                        verbose_name="is included",
                    ),
                ),
                (
                    "display_order",
                    models.PositiveIntegerField(
                        default=0,
                        help_text="Order in which features are displayed",
                        verbose_name="display order",
                    ),
                ),
                (
                    "plan",
                    models.ForeignKey(
                        help_text="Associated plan",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="plan_features",
                        to="billing.plan",
                        verbose_name="plan",
                    ),
                ),
            ],
            options={
                "verbose_name": "plan feature",
                "verbose_name_plural": "plan features",
                "ordering": ["plan", "display_order"],
                "unique_together": {("plan", "name")},
            },
        ),
        # Create PlanHistory model
        migrations.CreateModel(
            name="PlanHistory",
            fields=[
                (
                    "created_at",
                    models.DateTimeField(
                        db_index=True,
                        default=django.utils.timezone.now,
                        editable=False,
                        help_text="Date and time when the record was created",
                        verbose_name="created at",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True,
                        db_index=True,
                        help_text="Date and time when the record was last updated",
                        verbose_name="updated at",
                    ),
                ),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        help_text="Unique identifier",
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "change_type",
                    models.CharField(
                        help_text="Type of change (created, updated, deleted, etc.)",
                        max_length=20,
                        verbose_name="change type",
                    ),
                ),
                (
                    "changes",
                    models.TextField(
                        help_text="Description of changes made",
                        verbose_name="changes",
                    ),
                ),
                (
                    "snapshot",
                    models.JSONField(
                        blank=True,
                        null=True,
                        help_text="Full snapshot of plan data at time of change",
                        verbose_name="snapshot",
                    ),
                ),
                (
                    "plan",
                    models.ForeignKey(
                        help_text="Associated plan",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="history_records",
                        to="billing.plan",
                        verbose_name="plan",
                    ),
                ),
                (
                    "changed_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        help_text="User who made the change",
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="changed by",
                    ),
                ),
            ],
            options={
                "verbose_name": "plan history",
                "verbose_name_plural": "plan histories",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="planhistory",
            index=models.Index(
                fields=["plan", "-created_at"],
                name="billing_pla_plan_id_created_idx",
            ),
        ),
    ]
