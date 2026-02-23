"""
Subscription views: admin CRUD + user-facing subscription management.
"""
import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, DetailView, TemplateView, View

from tech_articles.billing.models import Plan, Subscription, PaymentTransaction
from tech_articles.billing.services import SubscriptionService
from tech_articles.utils.enums import PaymentProvider, PaymentStatus
from tech_articles.utils.mixins import AdminRequiredMixin

logger = logging.getLogger(__name__)


# ============================================================================
# ADMIN VIEWS
# ============================================================================

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
        context["status_choices"] = PaymentStatus.choices
        return context


class SubscriptionDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    """View subscription details (admin)."""
    model = Subscription
    template_name = "tech-articles/dashboard/pages/billing/subscriptions/detail.html"
    context_object_name = "subscription"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.contrib.contenttypes.models import ContentType
        sub_ct = ContentType.objects.get_for_model(Subscription)
        context["transactions"] = PaymentTransaction.objects.filter(
            content_type=sub_ct,
            object_id=str(self.object.id),
        ).order_by("-created_at")
        return context


# ============================================================================
# USER-FACING VIEWS (home / public-facing billing)
# ============================================================================

class PlanListPublicView(TemplateView):
    """Public plans listing page with subscribe CTAs."""
    template_name = "tech-articles/home/pages/billing/plans.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["plans"] = Plan.objects.filter(is_active=True).prefetch_related("plan_features").order_by("display_order", "price")
        if self.request.user.is_authenticated:
            context["active_subscription"] = SubscriptionService.get_active_subscription(self.request.user)
        return context


class PlanSubscribeView(LoginRequiredMixin, TemplateView):
    """
    Payment page: user selects Stripe (card/Apple Pay/Google Pay) or PayPal.
    On POST, creates a pending subscription + transaction.
    """
    template_name = "tech-articles/home/pages/billing/subscribe.html"

    def get_plan(self):
        return get_object_or_404(Plan, slug=self.kwargs["slug"], is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        plan = self.get_plan()
        context["plan"] = plan
        context["active_subscription"] = SubscriptionService.get_active_subscription(self.request.user)
        context["providers"] = [
            {"key": PaymentProvider.STRIPE, "label": "Stripe"},
            {"key": PaymentProvider.PAYPAL, "label": "PayPal"},
        ]
        return context

    def post(self, request, *args, **kwargs):
        plan = self.get_plan()
        provider = request.POST.get("provider", PaymentProvider.STRIPE)

        # Validate provider
        valid_providers = [PaymentProvider.STRIPE, PaymentProvider.PAYPAL]
        if provider not in valid_providers:
            messages.error(request, _("Invalid payment provider."))
            return redirect(request.path)

        # Check if user already has an active subscription to this plan
        existing = SubscriptionService.get_active_subscription(request.user)
        if existing and existing.plan_id == plan.id:
            messages.info(request, _("You are already subscribed to this plan."))
            return redirect("dashboard:my_subscription")

        try:
            subscription, payment_txn = SubscriptionService.initiate_subscription(
                user=request.user,
                plan=plan,
                provider=provider,
            )
            # In a real implementation, redirect to Stripe Checkout / PayPal order.
            # Here we store IDs in session and simulate a successful payment.
            request.session["pending_subscription_id"] = str(subscription.id)
            request.session["pending_txn_id"] = str(payment_txn.id)
            return redirect("billing:subscribe_confirm", slug=plan.slug)
        except Exception as exc:
            logger.exception("Error initiating subscription: %s", exc)
            messages.error(request, _("An error occurred. Please try again."))
            return redirect(request.path)


class PlanSubscribeConfirmView(LoginRequiredMixin, View):
    """
    Simulate payment confirmation (this would normally be a webhook or return URL).
    In production, replace this with your Stripe/PayPal confirmation handler.
    """

    def get(self, request, *args, **kwargs):
        plan = get_object_or_404(Plan, slug=kwargs["slug"], is_active=True)
        sub_id = request.session.pop("pending_subscription_id", None)
        txn_id = request.session.pop("pending_txn_id", None)

        if not sub_id or not txn_id:
            messages.error(request, _("No pending subscription found."))
            return redirect("billing:plans_public")

        try:
            subscription = Subscription.objects.get(id=sub_id, user=request.user)
            payment_txn = PaymentTransaction.objects.get(id=txn_id)
            SubscriptionService.confirm_subscription(
                subscription=subscription,
                payment_txn=payment_txn,
            )
            messages.success(
                request,
                _("You have successfully subscribed to the %(plan)s plan!") % {"plan": plan.name},
            )
        except Exception as exc:
            logger.exception("Error confirming subscription: %s", exc)
            messages.error(request, _("Payment confirmation failed. Please contact support."))

        return redirect("dashboard:my_subscription")


class SubscriptionCancelView(LoginRequiredMixin, View):
    """Cancel user's active subscription."""

    def post(self, request, *args, **kwargs):
        sub_id = kwargs["pk"]
        subscription = get_object_or_404(Subscription, id=sub_id, user=request.user)

        if subscription.status != PaymentStatus.SUCCEEDED:
            messages.error(request, _("This subscription is not active."))
            return redirect("dashboard:my_subscription")

        try:
            # Cancel at period end by default (user keeps access until period expires)
            SubscriptionService.cancel_subscription(subscription, at_period_end=True)
            messages.success(
                request,
                _("Your subscription has been cancelled. You will retain access until %(date)s.")
                % {"date": subscription.current_period_end.strftime("%B %d, %Y") if subscription.current_period_end else _("the end of the billing period")},
            )
        except Exception as exc:
            logger.exception("Error cancelling subscription: %s", exc)
            messages.error(request, _("Could not cancel subscription. Please try again."))

        return redirect("dashboard:my_subscription")


class SubscriptionChangePlanView(LoginRequiredMixin, View):
    """Allow user to change their current plan (upgrade/downgrade)."""

    def post(self, request, *args, **kwargs):
        new_plan_slug = request.POST.get("plan_slug")
        provider = request.POST.get("provider", PaymentProvider.STRIPE)

        if not new_plan_slug:
            messages.error(request, _("Please select a plan."))
            return redirect("dashboard:my_subscription")

        new_plan = get_object_or_404(Plan, slug=new_plan_slug, is_active=True)

        try:
            current_sub = SubscriptionService.get_active_subscription(request.user)
            subscription, payment_txn = SubscriptionService.change_plan(
                user=request.user,
                new_plan=new_plan,
                provider=provider,
                current_subscription=current_sub,
            )
            request.session["pending_subscription_id"] = str(subscription.id)
            request.session["pending_txn_id"] = str(payment_txn.id)
            return redirect("billing:subscribe_confirm", slug=new_plan.slug)
        except Exception as exc:
            logger.exception("Error changing plan: %s", exc)
            messages.error(request, _("Could not change plan. Please try again."))
            return redirect("dashboard:my_subscription")

