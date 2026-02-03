"""
Subscription views for dashboard CRUD operations.
"""
import logging

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView

from tech_articles.billing.models import Subscription

logger = logging.getLogger(__name__)


class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin that requires user to be an admin or staff."""

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


class SubscriptionListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """List all user subscriptions (admin view)."""
    model = Subscription
    template_name = "tech-articles/dashboard/pages/billing/subscriptions/list.html"
    context_object_name = "subscriptions"
    paginate_by = 10
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset().select_related("user", "plan")
        status = self.request.GET.get("status", "")

        if status:
            queryset = queryset.filter(status=status)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status"] = self.request.GET.get("status", "")
        return context


class SubscriptionDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    """View subscription details."""
    model = Subscription
    template_name = "tech-articles/dashboard/pages/billing/subscriptions/detail.html"
    context_object_name = "subscription"
