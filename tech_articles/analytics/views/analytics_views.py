"""
Analytics overview views for dashboard.
"""
import json
import logging
from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.utils import timezone
from django.views.generic import TemplateView

from tech_articles.analytics.models import Event
from tech_articles.analytics.services import AnalyticsKPI
from tech_articles.billing.models import PaymentTransaction
from tech_articles.utils.enums import PaymentStatus
from tech_articles.utils.mixins import AdminRequiredMixin

logger = logging.getLogger(__name__)


class AnalyticsOverviewView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """Analytics overview dashboard with real KPIs and ECharts."""
    template_name = "tech-articles/dashboard/pages/analytics/overview.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # KPIs
        context["total_events"] = Event.objects.count()
        context["events_this_month"] = AnalyticsKPI.get_events_this_month()
        context["total_revenue"] = PaymentTransaction.objects.filter(
            status=PaymentStatus.SUCCEEDED
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
        context["revenue_this_month"] = PaymentTransaction.objects.filter(
            status=PaymentStatus.SUCCEEDED,
            created_at__gte=month_start,
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

        # Chart data as JSON
        context["events_over_time_json"] = AnalyticsKPI.get_events_over_time(days=30)
        context["event_type_distribution_json"] = AnalyticsKPI.get_event_type_distribution()
        context["top_articles_json"] = AnalyticsKPI.get_top_articles(limit=10)
        context["user_growth_json"] = AnalyticsKPI.get_user_growth(months=12)
        context["revenue_over_time_json"] = AnalyticsKPI.get_revenue_over_time(days=30)

        return context

