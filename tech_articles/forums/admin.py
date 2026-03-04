from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import (
    ForumCategory,
    ForumThread,
    ThreadReply,
    ThreadAttachment,
    ThreadVote,
    ForumGroupAccess,
)


class ThreadAttachmentInline(admin.TabularInline):
    """Inline admin for thread attachments."""

    model = ThreadAttachment
    extra = 0
    fields = ["file", "original_filename", "uploaded_by", "created_at"]
    readonly_fields = ["created_at"]


class ThreadReplyInline(admin.TabularInline):
    """Inline admin for thread replies."""

    model = ThreadReply
    extra = 0
    fields = ["author", "content", "is_best_answer", "votes_count", "created_at"]
    readonly_fields = ["votes_count", "created_at"]
    show_change_link = True


@admin.register(ForumCategory)
class ForumCategoryAdmin(admin.ModelAdmin):
    """Admin interface for forum categories (groups)."""

    list_display = [
        "name",
        "is_active",
        "requires_subscription",
        "is_purchasable",
        "purchase_price",
        "purchase_currency",
        "display_order",
    ]
    list_filter = ["is_active", "requires_subscription", "is_purchasable", "purchase_currency"]
    search_fields = ["name", "slug", "description"]
    prepopulated_fields = {"slug": ("name",)}
    ordering = ["display_order", "name"]

    fieldsets = (
        (
            _("Basic Information"),
            {
                "fields": (
                    "name",
                    "slug",
                    "description",
                    "is_active",
                    "display_order",
                )
            },
        ),
        (
            _("SVG Icon"),
            {
                "fields": ("svg_icon",),
                "description": _(
                    "Paste raw SVG markup here. Use currentColor for fills/strokes "
                    "to enable automatic dark/light mode adaptation. "
                    "See FORUMS_SVG_GUIDE.md for detailed instructions."
                ),
            },
        ),
        (
            _("Access Control"),
            {
                "fields": (
                    "requires_subscription",
                    "is_purchasable",
                    "purchase_price",
                    "purchase_currency",
                )
            },
        ),
    )


@admin.register(ForumThread)
class ForumThreadAdmin(admin.ModelAdmin):
    """Admin interface for forum threads."""

    list_display = [
        "title",
        "category",
        "author",
        "is_pinned",
        "is_closed",
        "views_count",
        "created_at",
    ]
    list_filter = ["category", "is_pinned", "is_closed", "created_at"]
    search_fields = ["title", "content", "author__email", "author__username"]
    readonly_fields = ["views_count", "created_at", "updated_at"]
    ordering = ["-created_at"]
    inlines = [ThreadAttachmentInline, ThreadReplyInline]

    fieldsets = (
        (
            _("Thread"),
            {
                "fields": (
                    "category",
                    "author",
                    "title",
                    "content",
                )
            },
        ),
        (
            _("Status"),
            {
                "fields": (
                    "is_pinned",
                    "is_closed",
                    "views_count",
                    "deleted_at",
                )
            },
        ),
    )


@admin.register(ThreadReply)
class ThreadReplyAdmin(admin.ModelAdmin):
    """Admin interface for thread replies."""

    list_display = [
        "thread",
        "author",
        "is_best_answer",
        "votes_count",
        "created_at",
    ]
    list_filter = ["is_best_answer", "created_at"]
    search_fields = ["content", "author__email", "author__username", "thread__title"]
    readonly_fields = ["votes_count", "created_at", "updated_at"]
    ordering = ["-created_at"]
    inlines = [ThreadAttachmentInline]


@admin.register(ThreadAttachment)
class ThreadAttachmentAdmin(admin.ModelAdmin):
    """Admin interface for thread attachments."""

    list_display = ["original_filename", "uploaded_by", "thread", "reply", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["original_filename", "uploaded_by__email"]
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]


@admin.register(ThreadVote)
class ThreadVoteAdmin(admin.ModelAdmin):
    """Admin interface for thread votes (read-only)."""

    list_display = ["reply", "voter", "value", "created_at"]
    list_filter = ["value", "created_at"]
    search_fields = ["voter__email", "voter__username"]
    readonly_fields = ["reply", "voter", "value", "created_at", "updated_at"]
    ordering = ["-created_at"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(ForumGroupAccess)
class ForumGroupAccessAdmin(admin.ModelAdmin):
    """Admin interface for forum group access records."""

    list_display = [
        "user",
        "category",
        "status",
        "access_type",
        "payment_status",
        "amount_paid",
        "currency",
        "approved_at",
    ]
    list_filter = ["status", "access_type", "payment_status", "currency", "category"]
    search_fields = [
        "user__email",
        "user__username",
        "category__name",
        "provider_payment_id",
    ]
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]

    fieldsets = (
        (
            _("Access"),
            {
                "fields": (
                    "user",
                    "category",
                    "status",
                    "access_type",
                    "approved_at",
                    "approved_by",
                )
            },
        ),
        (
            _("Payment"),
            {
                "fields": (
                    "provider",
                    "payment_status",
                    "amount_paid",
                    "currency",
                    "provider_payment_id",
                )
            },
        ),
    )
