"""
Admin configuration for newsletter models.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from tech_articles.newsletter.models import (
    NewsletterSubscriber,
    NewsletterCampaign,
    EmailLog,
    SubscriberTag,
    SubscriberSegment,
    SubscriberEngagement,
    SubscriberTagAssignment,
)


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    """Admin for newsletter subscribers."""
    list_display = ["email", "language", "status", "is_confirmed", "is_active", "created_at"]
    list_filter = ["status", "language", "is_confirmed", "is_active", "created_at"]
    search_fields = ["email"]
    readonly_fields = ["id", "unsub_token", "confirm_token", "created_at", "updated_at"]
    
    fieldsets = (
        (_("Subscriber Information"), {
            "fields": ("email", "language", "status"),
        }),
        (_("Status"), {
            "fields": ("is_active", "is_confirmed", "confirmed_at"),
        }),
        (_("GDPR & Security"), {
            "fields": ("consent_given_at", "ip_address", "unsub_token", "confirm_token"),
        }),
        (_("Timestamps"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )


@admin.register(NewsletterCampaign)
class NewsletterCampaignAdmin(admin.ModelAdmin):
    """Admin for newsletter campaigns."""
    list_display = ["name", "schedule_mode", "is_active", "last_run_at", "created_at"]
    list_filter = ["is_active", "schedule_mode", "created_at"]
    search_fields = ["name"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    """Admin for email logs."""
    list_display = ["to_email", "subject", "status", "provider", "sent_at", "created_at"]
    list_filter = ["status", "provider", "created_at"]
    search_fields = ["to_email", "subject", "provider_message_id"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(SubscriberTag)
class SubscriberTagAdmin(admin.ModelAdmin):
    """Admin for subscriber tags."""
    list_display = ["name", "color", "created_at"]
    search_fields = ["name"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(SubscriberSegment)
class SubscriberSegmentAdmin(admin.ModelAdmin):
    """Admin for subscriber segments."""
    list_display = ["name", "created_at"]
    search_fields = ["name"]
    filter_horizontal = ["subscribers", "tags"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(SubscriberEngagement)
class SubscriberEngagementAdmin(admin.ModelAdmin):
    """Admin for subscriber engagement."""
    list_display = ["subscriber", "action", "created_at"]
    list_filter = ["action", "created_at"]
    search_fields = ["subscriber__email"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(SubscriberTagAssignment)
class SubscriberTagAssignmentAdmin(admin.ModelAdmin):
    """Admin for subscriber tag assignments."""
    list_display = ["subscriber", "tag", "created_at"]
    list_filter = ["tag", "created_at"]
    search_fields = ["subscriber__email", "tag__name"]
    readonly_fields = ["id", "created_at", "updated_at"]

