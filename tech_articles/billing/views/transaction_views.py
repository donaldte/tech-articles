"""
Transaction/Purchase views for dashboard.
"""
import logging

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView

from tech_articles.utils.mixins import AdminRequiredMixin

logger = logging.getLogger(__name__)



class TransactionListView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """List all transactions."""
    template_name = "tech-articles/dashboard/pages/billing/transactions/list.html"
