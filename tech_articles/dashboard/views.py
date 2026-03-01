"""
Dashboard views for Runbookly.
Contains views for both admin and regular user dashboards.
"""
import json
import logging
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Sum, Count
from django.utils import timezone
from django.views.generic import TemplateView

from tech_articles.accounts.models import User
from tech_articles.analytics.services import ReadingTracker
from tech_articles.appointments.models import Appointment
from tech_articles.billing.models import Plan, Subscription, PaymentTransaction
from tech_articles.billing.services import PurchaseService, SubscriptionService
from tech_articles.content.models import Article
from tech_articles.newsletter.models import NewsletterSubscriber
from tech_articles.utils.enums import PaymentStatus, AppointmentStatus

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_staff or user.is_superuser:
            self._build_admin_context(context)
        else:
            self._build_user_context(context, user)

        return context

    def _build_user_context(self, context, user):
        """Build dynamic context for the user dashboard."""
        now = timezone.now()

        # Active subscription
        active_sub = SubscriptionService.get_active_subscription(user)
        context["active_subscription"] = active_sub

        # Articles read this month
        reads_this_month = ReadingTracker.get_user_reads_this_month(user)
        reads_last_month = ReadingTracker.get_user_reads_last_month(user)
        context["articles_read_count"] = reads_this_month
        if reads_last_month > 0:
            context["articles_read_trend"] = round(
                ((reads_this_month - reads_last_month) / reads_last_month) * 100
            )
        else:
            context["articles_read_trend"] = 100 if reads_this_month > 0 else 0

        # Appointments
        user_appointments = Appointment.objects.filter(user=user)
        context["total_appointments"] = user_appointments.count()
        context["upcoming_appointments_count"] = user_appointments.filter(
            slot__start_at__gte=now,
            status=AppointmentStatus.CONFIRMED,
        ).count()

        # Upcoming appointments (detail)
        upcoming_appts = (
            user_appointments.filter(
                slot__start_at__gte=now,
                status__in=[AppointmentStatus.CONFIRMED, AppointmentStatus.PENDING],
            )
            .select_related("appointment_type", "slot")
            .order_by("slot__start_at")[:5]
        )
        context["upcoming_appointments"] = upcoming_appts

        # Recent reads
        context["recent_reads"] = ReadingTracker.get_recent_reads(user, limit=5)

        # Chart data
        chart_data = ReadingTracker.get_user_chart_data(user)
        context["chart_data_json"] = json.dumps(chart_data)

    def _build_admin_context(self, context):
        """Build dynamic context for the admin dashboard."""
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Total users
        total_users = User.objects.filter(is_active=True).count()
        context["total_users"] = total_users

        # New users this month
        new_users_month = User.objects.filter(
            is_active=True, date_joined__gte=month_start
        ).count()
        context["new_users_month"] = new_users_month

        # Active subscriptions
        active_subs = Subscription.objects.filter(
            status__in=[PaymentStatus.SUCCEEDED, PaymentStatus.FREE_ACCEPTED],
        ).count()
        context["active_subscriptions"] = active_subs

        # Conversion rate
        if total_users > 0:
            context["conversion_rate"] = round((active_subs / total_users) * 100)
        else:
            context["conversion_rate"] = 0

        # Monthly revenue
        monthly_revenue = PaymentTransaction.objects.filter(
            status=PaymentStatus.SUCCEEDED,
            created_at__gte=month_start,
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
        context["monthly_revenue"] = monthly_revenue

        # Last month revenue for comparison
        last_month_end = month_start - timedelta(seconds=1)
        last_month_start = last_month_end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month_revenue = PaymentTransaction.objects.filter(
            status=PaymentStatus.SUCCEEDED,
            created_at__gte=last_month_start,
            created_at__lte=last_month_end,
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
        if last_month_revenue > 0:
            context["revenue_trend"] = round(
                float((monthly_revenue - last_month_revenue) / last_month_revenue * 100)
            )
        else:
            context["revenue_trend"] = 100 if monthly_revenue > 0 else 0

        # Appointments this month
        appointments_month = Appointment.objects.filter(
            created_at__gte=month_start,
        ).count()
        context["appointments_month"] = appointments_month

        # Today's appointments
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        context["appointments_today"] = Appointment.objects.filter(
            slot__start_at__date=today_start.date(),
        ).count()

        # Subscription plan distribution
        plan_distribution = (
            Subscription.objects.filter(
                status__in=[PaymentStatus.SUCCEEDED, PaymentStatus.FREE_ACCEPTED],
            )
            .values("plan__name")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        context["plan_distribution_json"] = json.dumps(list(plan_distribution))

        # Revenue chart data
        chart_data = ReadingTracker.get_platform_chart_data()
        context["revenue_chart_data_json"] = json.dumps(chart_data)

        # Recent activity
        context["recent_activity"] = ReadingTracker.get_recent_platform_activity(limit=10)

        # Newsletter subscribers count
        context["newsletter_subscribers"] = NewsletterSubscriber.objects.filter(
            is_active=True
        ).count()

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
# USER PURCHASES VIEWS (All Users)
# =====================

class MyPurchasesView(LoginRequiredMixin, TemplateView):
    """View user's article purchase transactions with pagination and status filter."""
    template_name = "tech-articles/dashboard/pages/my-purchases/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        status_filter = self.request.GET.get("status", "")

        transactions = PurchaseService.get_user_purchase_transactions(user)
        if status_filter:
            transactions = transactions.filter(status=status_filter)

        paginator = Paginator(transactions, 10)
        page_number = self.request.GET.get("page", 1)
        page_obj = paginator.get_page(page_number)

        context["page_obj"] = page_obj
        context["status_filter"] = status_filter
        context["status_choices"] = PaymentStatus.choices
        return context


class MyArticlesView(LoginRequiredMixin, TemplateView):
    """View list of articles purchased by the user."""
    template_name = "tech-articles/dashboard/pages/my-articles/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        purchases = PurchaseService.get_user_purchases(self.request.user).filter(
            status=PaymentStatus.SUCCEEDED
        )
        paginator = Paginator(purchases, 12)
        page_number = self.request.GET.get("page", 1)
        context["page_obj"] = paginator.get_page(page_number)
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
# READING HISTORY
# =====================

class MyReadingHistoryView(LoginRequiredMixin, TemplateView):
    """View user's article reading history with pagination."""
    template_name = "tech-articles/dashboard/pages/reading-history/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        from tech_articles.analytics.models import Event
        from tech_articles.utils.enums import EventType
        import json as _json

        events = (
            Event.objects.filter(user=user, event_type=EventType.ARTICLE_READ)
            .order_by("-created_at")
        )

        # Build enriched list
        items = []
        seen_slugs = set()
        for event in events:
            try:
                meta = _json.loads(event.metadata_json) if event.metadata_json else {}
            except (_json.JSONDecodeError, TypeError):
                meta = {}
            slug = meta.get("article_slug", "")
            # Show all reads (not deduplicated) for full history
            article = None
            if slug:
                article = Article.objects.filter(slug=slug).first()
            items.append({
                "event": event,
                "meta": meta,
                "article": article,
            })

        paginator = Paginator(items, 15)
        page_number = self.request.GET.get("page", 1)
        context["page_obj"] = paginator.get_page(page_number)
        context["total_reads"] = len(items)
        return context


# =====================
# SUPPORT & HELP
# =====================

class SupportView(LoginRequiredMixin, TemplateView):
    """Technical support page."""
    template_name = "tech-articles/dashboard/pages/support/index.html"
