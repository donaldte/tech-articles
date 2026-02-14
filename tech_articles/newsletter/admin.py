"""
Newsletter admin configuration.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from tech_articles.newsletter.models import (
    NewsletterSubscriber,
    NewsletterCampaign,
    EmailLog,
)


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    """Admin interface for newsletter subscribers."""
    
    list_display = [
        "email",
        "language",
        "status",
        "is_active",
        "is_confirmed",
        "email_open_count",
        "email_click_count",
        "created_at",
    ]
    list_filter = [
        "status",
        "is_active",
        "is_confirmed",
        "language",
        "created_at",
    ]
    search_fields = ["email", "tags"]
    readonly_fields = [
        "unsub_token",
        "consent_given_at",
        "ip_address",
        "confirmed_at",
        "last_email_sent_at",
        "created_at",
        "updated_at",
    ]
    fieldsets = (
        (_("Basic Information"), {
            "fields": ("email", "language", "tags"),
        }),
        (_("Status"), {
            "fields": ("status", "is_active", "is_confirmed", "confirmed_at"),
        }),
        (_("Engagement"), {
            "fields": ("email_open_count", "email_click_count", "last_email_sent_at"),
        }),
        (_("GDPR & Privacy"), {
            "fields": ("consent_given_at", "ip_address", "unsub_token"),
        }),
        (_("Metadata"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )


@admin.register(NewsletterCampaign)
class NewsletterCampaignAdmin(admin.ModelAdmin):
    """Admin interface for newsletter campaigns."""
    
    list_display = [
        "name",
        "schedule_mode",
        "is_active",
        "last_run_at",
        "created_at",
    ]
    list_filter = ["is_active", "schedule_mode", "created_at"]
    search_fields = ["name", "template_subject"]
    readonly_fields = ["last_run_at", "created_at", "updated_at"]


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    """Admin interface for email logs."""
    
    list_display = [
        "to_email",
        "subject",
        "status",
        "provider",
        "sent_at",
        "created_at",
    ]
    list_filter = ["status", "provider", "created_at"]
    search_fields = ["to_email", "subject", "provider_message_id"]
    readonly_fields = ["created_at", "updated_at"]
