"""
Dashboard views for Runbookly.
Contains views for both admin and regular user dashboards.
"""
import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from tech_articles.appointments.models import Appointment
from tech_articles.billing.models import Plan
from tech_articles.billing.services import SubscriptionService

logger = logging.getLogger(__name__)


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
# USER SUBSCRIPTION VIEWS (All Users)
# =====================

class MySubscriptionView(LoginRequiredMixin, TemplateView):
    """View current subscription status and manage it."""
    template_name = "tech-articles/dashboard/pages/my-subscription/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["active_subscription"] = SubscriptionService.get_active_subscription(user)
        context["all_subscriptions"] = SubscriptionService.get_user_subscriptions(user)
        context["available_plans"] = Plan.objects.filter(is_active=True).prefetch_related("plan_features").order_by("display_order", "price")
        return context


class MyInvoicesView(LoginRequiredMixin, TemplateView):
    """View billing history and invoices."""
    template_name = "tech-articles/dashboard/pages/my-subscription/invoices.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["transactions"] = SubscriptionService.get_user_transactions(self.request.user)
        return context


# =====================
# USER APPOINTMENTS VIEWS (All Users)
# =====================

class MyAppointmentsView(LoginRequiredMixin, TemplateView):
    """View user's appointments."""
    template_name = "tech-articles/dashboard/pages/my-appointments/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["appointments"] = Appointment.objects.filter(
            user=self.request.user
        ).select_related('appointment_type', 'slot').order_by('-created_at')
        return context


class BookAppointmentView(LoginRequiredMixin, TemplateView):
    """Book a new appointment."""
    template_name = "tech-articles/dashboard/pages/my-appointments/book.html"


# =====================
# SUPPORT & HELP
# =====================

class SupportView(LoginRequiredMixin, TemplateView):
    """Technical support page."""
    template_name = "tech-articles/dashboard/pages/support/index.html"
