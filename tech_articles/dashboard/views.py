"""
Dashboard views for Runbookly.
Contains views for both admin and regular user dashboards.
"""
import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView

from tech_articles.billing.models import Plan, PlanFeature, Coupon, Subscription, PlanHistory
from tech_articles.billing.forms import PlanForm, PlanFeatureForm, CouponForm

logger = logging.getLogger(__name__)



class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin that requires user to be an admin or staff."""

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


# =====================
# NAVIGATION VIEWS
# =====================

class DashboardPageView(LoginRequiredMixin, TemplateView):
    """
    Main dashboard home page.
    Shows overview statistics and quick actions.
    """
    template_name = "tech-articles/dashboard/pages/index.html"


# =====================
# CONTENT MANAGEMENT (Admin)
# =====================

class ArticleListView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """List all articles for admin management."""
    template_name = "tech-articles/dashboard/pages/content/articles/list.html"


class ArticleCreateView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """Create a new article."""
    template_name = "tech-articles/dashboard/pages/content/articles/create.html"


# Note: CategoryListView, CategoryCreateView, TagListView, TagCreateView
# have been moved to tech_articles.content.views module with full CRUD support


# =====================
# RESOURCES MANAGEMENT (Admin)
# =====================

class ResourceListView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """List all resources/documents for admin management."""
    template_name = "tech-articles/dashboard/pages/resources/list.html"


class ResourceCreateView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """Upload a new resource/document."""
    template_name = "tech-articles/dashboard/pages/resources/create.html"


# =====================
# APPOINTMENTS MANAGEMENT (Admin)
# =====================

class AppointmentTypeListView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """List all appointment types for admin management."""
    template_name = "tech-articles/dashboard/pages/appointments/types/list.html"


class AppointmentTypeCreateView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """Create a new appointment type."""
    template_name = "tech-articles/dashboard/pages/appointments/types/create.html"


class AvailabilitySettingsView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """Manage availability settings."""
    template_name = "tech-articles/dashboard/pages/appointments/availability.html"


class AppointmentListView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """List all appointments (admin view)."""
    template_name = "tech-articles/dashboard/pages/appointments/list.html"


# =====================
# BILLING & SUBSCRIPTIONS (Admin)
# =====================

class PlanListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """List all subscription plans."""
    model = Plan
    template_name = "tech-articles/dashboard/pages/billing/plans/list.html"
    context_object_name = "plans"
    paginate_by = 20

    def get_queryset(self):
        """Get plans ordered by display order."""
        return Plan.objects.all().prefetch_related("plan_features")


class PlanCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    """Create a new subscription plan."""
    model = Plan
    form_class = PlanForm
    template_name = "tech-articles/dashboard/pages/billing/plans/create.html"
    success_url = reverse_lazy("dashboard:plans_list")

    def form_valid(self, form):
        """Save plan and create history record."""
        response = super().form_valid(form)
        
        # Create history record
        PlanHistory.objects.create(
            plan=self.object,
            changed_by=self.request.user,
            change_type="created",
            changes=_("Plan created"),
            snapshot={
                "name": self.object.name,
                "price": str(self.object.price),
                "interval": self.object.interval,
                "is_active": self.object.is_active,
            },
        )
        
        messages.success(self.request, _("Plan created successfully."))
        return response

    def form_invalid(self, form):
        """Handle invalid form."""
        messages.error(self.request, _("Please correct the errors below."))
        return super().form_invalid(form)


class PlanUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    """Update an existing subscription plan."""
    model = Plan
    form_class = PlanForm
    template_name = "tech-articles/dashboard/pages/billing/plans/edit.html"
    success_url = reverse_lazy("dashboard:plans_list")

    def get_context_data(self, **kwargs):
        """Add features and history to context."""
        context = super().get_context_data(**kwargs)
        
        # Prepare features data for JavaScript consumption
        # json_script filter will handle JSON serialization and proper type conversion
        features = self.object.plan_features.all()
        features_list = [
            {
                "id": str(feature.id),  # UUID must be converted to string for JSON
                "name": feature.name,
                "description": feature.description or "",  # Defensive: ensure empty string not None
                "is_included": feature.is_included,
                "display_order": feature.display_order,
            }
            for feature in features
        ]
        
        context["features"] = features  # Keep for template display
        context["features_list"] = features_list  # For json_script in template
        context["history"] = self.object.history_records.all()[:10]
        return context

    def form_valid(self, form):
        """Save plan and create history record."""
        # Get old values before saving
        old_plan = Plan.objects.get(pk=self.object.pk)
        changes = []
        
        for field in ["name", "price", "interval", "is_active"]:
            old_value = getattr(old_plan, field)
            new_value = form.cleaned_data.get(field)
            if old_value != new_value:
                changes.append(f"{field}: {old_value} -> {new_value}")
        
        response = super().form_valid(form)
        
        # Create history record if there are changes
        if changes:
            PlanHistory.objects.create(
                plan=self.object,
                changed_by=self.request.user,
                change_type="updated",
                changes="; ".join(changes),
                snapshot={
                    "name": self.object.name,
                    "price": str(self.object.price),
                    "interval": self.object.interval,
                    "is_active": self.object.is_active,
                },
            )
        
        messages.success(self.request, _("Plan updated successfully."))
        return response

    def form_invalid(self, form):
        """Handle invalid form."""
        messages.error(self.request, _("Please correct the errors below."))
        return super().form_invalid(form)


class PlanDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    """Delete a subscription plan."""
    model = Plan
    template_name = "tech-articles/dashboard/pages/billing/plans/delete.html"
    success_url = reverse_lazy("dashboard:plans_list")

    def form_valid(self, form):
        """Create history record before deleting."""
        PlanHistory.objects.create(
            plan=self.object,
            changed_by=self.request.user,
            change_type="deleted",
            changes=_("Plan deleted"),
            snapshot={
                "name": self.object.name,
                "price": str(self.object.price),
                "interval": self.object.interval,
            },
        )
        
        messages.success(self.request, _("Plan deleted successfully."))
        return super().form_valid(form)


class CouponListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """List all discount coupons."""
    model = Coupon
    template_name = "tech-articles/dashboard/pages/billing/coupons/list.html"
    context_object_name = "coupons"
    paginate_by = 20


class CouponCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    """Create a new discount coupon."""
    model = Coupon
    form_class = CouponForm
    template_name = "tech-articles/dashboard/pages/billing/coupons/create.html"
    success_url = reverse_lazy("dashboard:coupons_list")

    def form_valid(self, form):
        """Save coupon."""
        messages.success(self.request, _("Coupon created successfully."))
        return super().form_valid(form)

    def form_invalid(self, form):
        """Handle invalid form."""
        messages.error(self.request, _("Please correct the errors below."))
        return super().form_invalid(form)


class CouponUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    """Update an existing coupon."""
    model = Coupon
    form_class = CouponForm
    template_name = "tech-articles/dashboard/pages/billing/coupons/edit.html"
    success_url = reverse_lazy("dashboard:coupons_list")

    def form_valid(self, form):
        """Save coupon."""
        messages.success(self.request, _("Coupon updated successfully."))
        return super().form_valid(form)

    def form_invalid(self, form):
        """Handle invalid form."""
        messages.error(self.request, _("Please correct the errors below."))
        return super().form_invalid(form)


class TransactionListView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """List all transactions."""
    template_name = "tech-articles/dashboard/pages/billing/transactions/list.html"


class SubscriptionListView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """List all user subscriptions (admin view)."""
    template_name = "tech-articles/dashboard/pages/billing/subscriptions/list.html"


# =====================
# NEWSLETTER MANAGEMENT (Admin)
# =====================

class SubscriberListView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """List all newsletter subscribers."""
    template_name = "tech-articles/dashboard/pages/newsletter/subscribers/list.html"


class CampaignListView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """List all newsletter campaigns."""
    template_name = "tech-articles/dashboard/pages/newsletter/campaigns/list.html"


class CampaignCreateView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """Create a new newsletter campaign."""
    template_name = "tech-articles/dashboard/pages/newsletter/campaigns/create.html"


# =====================
# ANALYTICS (Admin)
# =====================

class AnalyticsOverviewView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """Analytics overview dashboard."""
    template_name = "tech-articles/dashboard/pages/analytics/overview.html"


class EventsListView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """List tracked events."""
    template_name = "tech-articles/dashboard/pages/analytics/events.html"


# =====================
# USER MANAGEMENT (Admin) - Moved to accounts app
# =====================
# UserListView, UserCreateView, UserDetailView, UserUpdateView,
# UserDeleteView, UserPasswordChangeView are now in tech_articles.accounts.views


# =====================
# USER PROFILE VIEWS (All Users) - Moved to accounts app
# =====================
# ProfileEditView, ProfileSecurityView, ProfileAvatarUploadView,
# ProfileAvatarDeleteView are now in tech_articles.accounts.views


# =====================
# USER SUBSCRIPTION VIEWS (All Users)
# =====================

class MySubscriptionView(LoginRequiredMixin, TemplateView):
    """View current subscription status."""
    template_name = "tech-articles/dashboard/pages/my-subscription/index.html"


class MyInvoicesView(LoginRequiredMixin, TemplateView):
    """View billing history and invoices."""
    template_name = "tech-articles/dashboard/pages/my-subscription/invoices.html"


# =====================
# USER APPOINTMENTS VIEWS (All Users)
# =====================

class MyAppointmentsView(LoginRequiredMixin, TemplateView):
    """View user's appointments."""
    template_name = "tech-articles/dashboard/pages/my-appointments/list.html"


class BookAppointmentView(LoginRequiredMixin, TemplateView):
    """Book a new appointment."""
    template_name = "tech-articles/dashboard/pages/my-appointments/book.html"


# =====================
# SUPPORT & HELP
# =====================

class SupportView(LoginRequiredMixin, TemplateView):
    """Technical support page."""
    template_name = "tech-articles/dashboard/pages/support/index.html"
