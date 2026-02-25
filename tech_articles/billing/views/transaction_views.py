"""
Transaction/Purchase views for dashboard.
"""
import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView

from tech_articles.billing.models import PaymentTransaction
from tech_articles.utils.enums import PaymentProvider, PaymentStatus
from tech_articles.utils.mixins import AdminRequiredMixin

logger = logging.getLogger(__name__)


class TransactionListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """List all payment transactions with filtering and pagination (admin)."""

    model = PaymentTransaction
    template_name = "tech-articles/dashboard/pages/billing/transactions/list.html"
    context_object_name = "transactions"
    paginate_by = 25
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = PaymentTransaction.objects.select_related("content_type").order_by("-created_at")

        # Filter: status
        status = self.request.GET.get("status", "")
        if status:
            qs = qs.filter(status=status)

        # Filter: gateway / provider
        gateway = self.request.GET.get("gateway", "")
        if gateway:
            qs = qs.filter(provider=gateway)

        # Filter: date range
        date_from = self.request.GET.get("date_from", "")
        date_to = self.request.GET.get("date_to", "")
        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)

        # Search: transaction id / provider payment id / provider subscription id
        search = self.request.GET.get("search", "").strip()
        if search:
            qs = qs.filter(
                Q(id__icontains=search)
                | Q(provider_payment_id__icontains=search)
                | Q(provider_subscription_id__icontains=search)
                | Q(idempotency_key__icontains=search)
            )

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status"] = self.request.GET.get("status", "")
        context["gateway"] = self.request.GET.get("gateway", "")
        context["date_from"] = self.request.GET.get("date_from", "")
        context["date_to"] = self.request.GET.get("date_to", "")
        context["search"] = self.request.GET.get("search", "")
        context["status_choices"] = PaymentStatus.choices
        context["gateway_choices"] = PaymentProvider.choices
        context["total_count"] = PaymentTransaction.objects.count()
        return context
