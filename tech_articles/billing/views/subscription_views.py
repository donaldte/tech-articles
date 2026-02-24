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
from tech_articles.billing.services import SubscriptionService, StripeService, PayPalService
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
        from decimal import Decimal
        plan = self.get_plan()
        provider = request.POST.get("provider", PaymentProvider.STRIPE)

        # Check if user already has an active subscription to this plan
        existing = SubscriptionService.get_active_subscription(request.user)
        if existing and existing.plan_id == plan.id:
            messages.info(request, _("You are already subscribed to this plan."))
            return redirect("dashboard:my_subscription")

        # ── Free plan: skip payment entirely ──────────────────────────
        if plan.price == Decimal("0.00") or plan.price == 0:
            try:
                SubscriptionService.subscribe_free(request.user, plan)
                messages.success(
                    request,
                    _("You have successfully subscribed to the %(plan)s plan!") % {"plan": plan.name},
                )
                return redirect("dashboard:my_subscription")
            except Exception as exc:
                logger.exception("Error subscribing to free plan: %s", exc)
                messages.error(request, _("An error occurred. Please try again."))
                return redirect(request.path)

        # ── Paid plan ─────────────────────────────────────────────────
        # Validate provider
        valid_providers = [PaymentProvider.STRIPE, PaymentProvider.PAYPAL]
        if provider not in valid_providers:
            messages.error(request, _("Invalid payment provider."))
            return redirect(request.path)

        try:
            subscription, payment_txn = SubscriptionService.initiate_subscription(
                user=request.user,
                plan=plan,
                provider=provider,
            )

            if provider == PaymentProvider.STRIPE:
                checkout_url = StripeService.create_checkout_session(
                    subscription=subscription,
                    payment_txn=payment_txn,
                    request=request,
                )
                return redirect(checkout_url)

            if provider == PaymentProvider.PAYPAL:
                approval_url = PayPalService.create_subscription(
                    subscription=subscription,
                    payment_txn=payment_txn,
                    request=request,
                )
                return redirect(approval_url)

        except Exception as exc:
            logger.exception("Error initiating subscription: %s", exc)
            messages.error(request, _("An error occurred. Please try again."))
            return redirect(request.path)


class StripeSuccessView(LoginRequiredMixin, View):
    """
    Stripe Checkout success return URL.
    The actual activation is handled by the webhook; this page just informs the user.
    """

    def get(self, request, *args, **kwargs):
        session_id = request.GET.get("session_id", "")
        if session_id:
            try:
                session = StripeService.retrieve_checkout_session(session_id)
                metadata = session.get("metadata", {})
                sub_id = metadata.get("subscription_id")
                txn_id = metadata.get("payment_txn_id")
                if sub_id and txn_id:
                    # Activate immediately for Stripe Checkout (webhook may arrive later)
                    subscription = Subscription.objects.filter(id=sub_id, user=request.user).first()
                    payment_txn = PaymentTransaction.objects.filter(id=txn_id).first()
                    if subscription and payment_txn and subscription.status == PaymentStatus.PENDING:
                        stripe_sub_id = session.get("subscription", "")
                        SubscriptionService.confirm_subscription(
                            subscription=subscription,
                            payment_txn=payment_txn,
                            provider_subscription_id=stripe_sub_id,
                            provider_payment_id=session_id,
                        )
            except Exception as exc:
                logger.warning("Stripe success callback processing error: %s", exc)

        messages.success(
            request,
            _("Payment successful! Your subscription is now active."),
        )
        return redirect("dashboard:my_subscription")


class PayPalReturnView(LoginRequiredMixin, View):
    """
    PayPal subscription return URL (user approves on PayPal and comes back here).
    """

    def get(self, request, *args, **kwargs):
        # Our internal IDs passed via return_url query params
        sub_id = request.GET.get("subscription_id", "")
        txn_id = request.GET.get("txn_id", "")

        try:
            subscription = Subscription.objects.get(id=sub_id, user=request.user)
            payment_txn = PaymentTransaction.objects.get(id=txn_id)

            if subscription.status == PaymentStatus.PENDING:
                # Verify with PayPal that the subscription is active
                if payment_txn.provider_subscription_id:
                    details = PayPalService.get_subscription_details(payment_txn.provider_subscription_id)
                    if details.get("status") in ("ACTIVE", "APPROVED"):
                        SubscriptionService.confirm_subscription(
                            subscription=subscription,
                            payment_txn=payment_txn,
                            provider_subscription_id=payment_txn.provider_subscription_id,
                            raw=details,
                        )
            messages.success(
                request,
                _("Payment successful! Your subscription is now active."),
            )
        except Exception as exc:
            logger.exception("PayPal return processing error: %s", exc)
            messages.error(request, _("Could not confirm your PayPal subscription. Please contact support."))

        return redirect("dashboard:my_subscription")


class PlanSubscribeConfirmView(LoginRequiredMixin, View):
    """Legacy confirm view — kept for backward compatibility (no longer used in normal flow)."""

    def get(self, request, *args, **kwargs):
        messages.info(request, _("Please use the payment provider checkout to subscribe."))
        return redirect("billing:plans_public")


class SubscriptionCancelView(LoginRequiredMixin, View):
    """Cancel user's active subscription."""

    def post(self, request, *args, **kwargs):
        sub_id = kwargs["pk"]
        subscription = get_object_or_404(Subscription, id=sub_id, user=request.user)

        active_statuses = [PaymentStatus.SUCCEEDED, PaymentStatus.FREE_ACCEPTED]
        if subscription.status not in active_statuses:
            messages.error(request, _("This subscription is not active."))
            return redirect("dashboard:my_subscription")

        try:
            SubscriptionService.cancel_subscription(subscription, at_period_end=True)
            if subscription.status == PaymentStatus.FREE_ACCEPTED:
                messages.success(request, _("Your free subscription has been cancelled."))
            else:
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
        from decimal import Decimal
        new_plan_slug = request.POST.get("plan_slug")
        provider = request.POST.get("provider", PaymentProvider.STRIPE)

        if not new_plan_slug:
            messages.error(request, _("Please select a plan."))
            return redirect("dashboard:my_subscription")

        new_plan = get_object_or_404(Plan, slug=new_plan_slug, is_active=True)

        try:
            current_sub = SubscriptionService.get_active_subscription(request.user)
            result = SubscriptionService.change_plan(
                user=request.user,
                new_plan=new_plan,
                provider=provider,
                current_subscription=current_sub,
            )

            # Free plan — result is a Subscription with no PaymentTransaction
            if isinstance(result, Subscription):
                messages.success(
                    request,
                    _("You have successfully switched to the %(plan)s plan!") % {"plan": new_plan.name},
                )
                return redirect("dashboard:my_subscription")

            # Paid plan — result is (Subscription, PaymentTransaction)
            subscription, payment_txn = result
            if provider == PaymentProvider.STRIPE:
                checkout_url = StripeService.create_checkout_session(
                    subscription=subscription,
                    payment_txn=payment_txn,
                    request=request,
                )
                return redirect(checkout_url)

            if provider == PaymentProvider.PAYPAL:
                approval_url = PayPalService.create_subscription(
                    subscription=subscription,
                    payment_txn=payment_txn,
                    request=request,
                )
                return redirect(approval_url)

        except Exception as exc:
            logger.exception("Error changing plan: %s", exc)
            messages.error(request, _("Could not change plan. Please try again."))
            return redirect("dashboard:my_subscription")

