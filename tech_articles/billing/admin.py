from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Plan, PlanFeature, PlanHistory, Subscription, Purchase, Coupon


class PlanFeatureInline(admin.TabularInline):
    """Inline admin for plan features."""
    model = PlanFeature
    extra = 1
    fields = ["name", "description", "is_included", "display_order"]
    ordering = ["display_order"]


class PlanHistoryInline(admin.TabularInline):
    """Inline admin for plan history."""
    model = PlanHistory
    extra = 0
    readonly_fields = ["created_at", "changed_by", "change_type", "changes"]
    fields = ["created_at", "changed_by", "change_type", "changes"]
    can_delete = False
    ordering = ["-created_at"]

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    """Admin interface for subscription plans."""
    list_display = [
        "name",
        "price",
        "currency",
        "interval",
        "is_active",
        "is_popular",
        "display_order",
        "trial_period_days",
    ]
    list_filter = ["is_active", "is_popular", "interval", "currency"]
    search_fields = ["name", "slug", "description"]
    prepopulated_fields = {"slug": ("name",)}
    ordering = ["display_order", "price"]
    inlines = [PlanFeatureInline, PlanHistoryInline]

    fieldsets = (
        (
            _("Basic Information"),
            {
                "fields": (
                    "name",
                    "slug",
                    "description",
                    "is_active",
                    "is_popular",
                    "display_order",
                )
            },
        ),
        (
            _("Pricing"),
            {
                "fields": (
                    "price",
                    "currency",
                    "interval",
                    "custom_interval_count",
                )
            },
        ),
        (
            _("Trial & Limits"),
            {
                "fields": (
                    "trial_period_days",
                    "max_articles",
                    "max_resources",
                    "max_appointments",
                )
            },
        ),
        (
            _("Payment Provider"),
            {
                "fields": (
                    "provider",
                    "provider_price_id",
                )
            },
        ),
        (
            _("Features (JSON - Legacy)"),
            {
                "fields": ("features_json",),
                "classes": ("collapse",),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        """Save the plan and create a history record."""
        if change:
            change_type = "updated"
            changes = "Plan updated"
        else:
            change_type = "created"
            changes = "Plan created"

        super().save_model(request, obj, form, change)

        # Create history record
        PlanHistory.objects.create(
            plan=obj,
            changed_by=request.user,
            change_type=change_type,
            changes=changes,
            snapshot={
                "name": obj.name,
                "price": str(obj.price),
                "interval": obj.interval,
                "is_active": obj.is_active,
            },
        )


@admin.register(PlanFeature)
class PlanFeatureAdmin(admin.ModelAdmin):
    """Admin interface for plan features."""
    list_display = ["plan", "name", "is_included", "display_order"]
    list_filter = ["plan", "is_included"]
    search_fields = ["name", "description"]
    ordering = ["plan", "display_order"]


@admin.register(PlanHistory)
class PlanHistoryAdmin(admin.ModelAdmin):
    """Admin interface for plan history (read-only)."""
    list_display = ["plan", "change_type", "changed_by", "created_at"]
    list_filter = ["change_type", "created_at"]
    search_fields = ["plan__name", "changes"]
    readonly_fields = ["plan", "changed_by", "change_type", "changes", "snapshot", "created_at"]
    ordering = ["-created_at"]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Admin interface for subscriptions."""
    list_display = ["user", "plan", "status", "current_period_start", "current_period_end"]
    list_filter = ["status", "plan", "provider"]
    search_fields = ["user__email", "user__username", "plan__name"]
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    """Admin interface for purchases."""
    list_display = ["user", "article", "amount", "currency", "status", "created_at"]
    list_filter = ["status", "provider", "currency"]
    search_fields = ["user__email", "user__username", "article__title"]
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    """Admin interface for coupons."""
    list_display = [
        "code",
        "coupon_type",
        "get_value_display",
        "is_active",
        "used_count",
        "max_uses",
        "expires_at",
    ]
    list_filter = ["is_active", "coupon_type", "currency"]
    search_fields = ["code"]
    readonly_fields = ["used_count", "created_at", "updated_at"]
    ordering = ["-created_at"]

    fieldsets = (
        (
            _("Coupon Information"),
            {
                "fields": (
                    "code",
                    "is_active",
                )
            },
        ),
        (
            _("Discount Value"),
            {
                "fields": (
                    "coupon_type",
                    "value_percent",
                    "value_amount",
                    "currency",
                )
            },
        ),
        (
            _("Usage & Expiration"),
            {
                "fields": (
                    "max_uses",
                    "used_count",
                    "expires_at",
                )
            },
        ),
    )

    def get_value_display(self, obj):
        """Display the coupon value."""
        if obj.coupon_type == "percent":
            return f"{obj.value_percent}%"
        return f"{obj.value_amount} {obj.currency}"
    get_value_display.short_description = _("Value")

