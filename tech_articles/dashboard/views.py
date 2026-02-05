"""
Dashboard views for Runbookly.
Contains views for both admin and regular user dashboards.
"""
import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

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
