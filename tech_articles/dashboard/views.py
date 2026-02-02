"""
Dashboard views for Runbookly.
Contains views for both admin and regular user dashboards.
"""
import logging

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView
from django.utils.translation import gettext_lazy as _

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

class PlanListView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """List all subscription plans."""
    template_name = "tech-articles/dashboard/pages/billing/plans/list.html"


class PlanCreateView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """Create a new subscription plan."""
    template_name = "tech-articles/dashboard/pages/billing/plans/create.html"


class CouponListView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """List all discount coupons."""
    template_name = "tech-articles/dashboard/pages/billing/coupons/list.html"


class CouponCreateView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """Create a new discount coupon."""
    template_name = "tech-articles/dashboard/pages/billing/coupons/create.html"


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
