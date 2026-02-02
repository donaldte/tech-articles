# Generated manually for newsletter subscriber management

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("newsletter", "0001_initial"),
    ]

    operations = [
        # Add new fields to NewsletterSubscriber
        migrations.AddField(
            model_name="newslettersubscriber",
            name="status",
            field=models.CharField(
                choices=[
                    ("active", "Active"),
                    ("inactive", "Inactive"),
                    ("bounced", "Bounced"),
                    ("unsubscribed", "Unsubscribed"),
                ],
                db_index=True,
                default="active",
                help_text="Current subscriber status",
                max_length=20,
                verbose_name="status",
            ),
        ),
        migrations.AddField(
            model_name="newslettersubscriber",
            name="confirm_token",
            field=models.CharField(
                db_index=True,
                default="",
                editable=False,
                help_text="Token for email confirmation (double opt-in)",
                max_length=64,
                unique=True,
                verbose_name="confirmation token",
            ),
        ),
        migrations.AddField(
            model_name="newslettersubscriber",
            name="consent_given_at",
            field=models.DateTimeField(
                blank=True,
                help_text="Date and time when GDPR consent was given",
                null=True,
                verbose_name="consent given at",
            ),
        ),
        migrations.AddField(
            model_name="newslettersubscriber",
            name="ip_address",
            field=models.GenericIPAddressField(
                blank=True,
                help_text="IP address used during subscription",
                null=True,
                verbose_name="IP address",
            ),
        ),
        # Create new models
        migrations.CreateModel(
            name="SubscriberTag",
            fields=[
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        db_index=True,
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
                        help_text="Tag name",
                        max_length=50,
                        unique=True,
                        verbose_name="name",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        default="",
                        help_text="Tag description",
                        verbose_name="description",
                    ),
                ),
                (
                    "color",
                    models.CharField(
                        default="#3B82F6",
                        help_text="Tag color in hex format",
                        max_length=7,
                        verbose_name="color",
                    ),
                ),
            ],
            options={
                "verbose_name": "subscriber tag",
                "verbose_name_plural": "subscriber tags",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="SubscriberSegment",
            fields=[
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        db_index=True,
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
                        help_text="Segment name",
                        max_length=100,
                        unique=True,
                        verbose_name="name",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        default="",
                        help_text="Segment description",
                        verbose_name="description",
                    ),
                ),
                (
                    "subscribers",
                    models.ManyToManyField(
                        blank=True,
                        related_name="segments",
                        to="newsletter.newslettersubscriber",
                        verbose_name="subscribers",
                    ),
                ),
                (
                    "tags",
                    models.ManyToManyField(
                        blank=True,
                        related_name="segments",
                        to="newsletter.subscribertag",
                        verbose_name="tags",
                    ),
                ),
            ],
            options={
                "verbose_name": "subscriber segment",
                "verbose_name_plural": "subscriber segments",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="SubscriberEngagement",
            fields=[
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        db_index=True,
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
                    "action",
                    models.CharField(
                        help_text="Engagement action (opened, clicked, etc.)",
                        max_length=30,
                        verbose_name="action",
                    ),
                ),
                (
                    "metadata",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        help_text="Additional engagement data",
                        verbose_name="metadata",
                    ),
                ),
                (
                    "subscriber",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="engagements",
                        to="newsletter.newslettersubscriber",
                        verbose_name="subscriber",
                    ),
                ),
                (
                    "email_log",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="engagements",
                        to="newsletter.emaillog",
                        verbose_name="email log",
                    ),
                ),
            ],
            options={
                "verbose_name": "subscriber engagement",
                "verbose_name_plural": "subscriber engagements",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="SubscriberTagAssignment",
            fields=[
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        db_index=True,
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
                    "subscriber",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tag_assignments",
                        to="newsletter.newslettersubscriber",
                        verbose_name="subscriber",
                    ),
                ),
                (
                    "tag",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="assignments",
                        to="newsletter.subscribertag",
                        verbose_name="tag",
                    ),
                ),
            ],
            options={
                "verbose_name": "subscriber tag assignment",
                "verbose_name_plural": "subscriber tag assignments",
                "ordering": ["-created_at"],
                "unique_together": {("subscriber", "tag")},
            },
        ),
        # Add indexes
        migrations.AddIndex(
            model_name="newslettersubscriber",
            index=models.Index(
                fields=["status", "is_confirmed"],
                name="newsletter_s_status_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="subscriberengagement",
            index=models.Index(
                fields=["subscriber", "action"],
                name="newsletter_s_sub_action_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="subscriberengagement",
            index=models.Index(
                fields=["action", "created_at"],
                name="newsletter_s_action_created_idx",
            ),
        ),
    ]
