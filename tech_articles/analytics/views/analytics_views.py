"""
Analytics overview views for dashboard.
"""
import logging

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView

logger = logging.getLogger(__name__)


class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin that requires user to be an admin or staff."""

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


class AnalyticsOverviewView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """Analytics overview dashboard."""
    template_name = "tech-articles/dashboard/pages/analytics/overview.html"
