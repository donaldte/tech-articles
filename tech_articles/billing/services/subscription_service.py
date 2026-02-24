"""
Subscription service: business logic for subscribing, changing, and cancelling plans.
Payment provider integration (Stripe / PayPal) will be wired here.
"""
from __future__ import annotations

import uuid
import logging
from decimal import Decimal
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from tech_articles.billing.models import Plan, Subscription, PaymentTransaction
from tech_articles.utils.enums import PaymentProvider, PaymentStatus

logger = logging.getLogger(__name__)


class SubscriptionService:
    """Handles subscription lifecycle: create, change plan, cancel."""

    # ------------------------------------------------------------------
    # Read helpers
    # ------------------------------------------------------------------

    @staticmethod
    def get_active_subscription(user) -> Subscription | None:
        """Return the user's current active (paid or free) subscription or None."""
        return (
            Subscription.objects.filter(
                user=user,
                status__in=[PaymentStatus.SUCCEEDED, PaymentStatus.FREE_ACCEPTED],
            )
            .select_related("plan")
            .order_by("-created_at")
            .first()
        )

    @staticmethod
    def get_user_subscriptions(user):
        """Return all subscriptions for a user ordered by date."""
        return (
            Subscription.objects.filter(user=user)
            .select_related("plan")
            .order_by("-created_at")
        )

    @staticmethod
    def get_user_transactions(user):
        """Return PaymentTransactions linked to the user's subscriptions."""
        sub_ct = ContentType.objects.get_for_model(Subscription)
        sub_ids = [
            str(s.id)
            for s in Subscription.objects.filter(user=user).values_list("id", flat=True)
        ]
        return PaymentTransaction.objects.filter(
            content_type=sub_ct,
            object_id__in=sub_ids,
        ).order_by("-created_at")

    # ------------------------------------------------------------------
    # Write helpers
    # ------------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def subscribe_free(user, plan: Plan) -> Subscription:
        """
        Immediately activate a free plan (price == 0). No payment required.
        The subscription has no expiration date.
        """
        now = timezone.now()
        subscription = Subscription.objects.create(
            user=user,
            plan=plan,
            provider="",
            status=PaymentStatus.FREE_ACCEPTED,
            current_period_start=now,
            current_period_end=None,  # free plans do not expire
        )
        logger.info(
            "Free subscription activated %s for user %s (plan: %s)",
            subscription.id,
            user.id,
            plan.name,
        )
        return subscription

    @staticmethod
    @transaction.atomic
    def initiate_subscription(user, plan: Plan, provider: str) -> tuple[Subscription, PaymentTransaction]:
        """
        Create a pending Subscription and a pending PaymentTransaction.
        Returns (subscription, transaction) — the caller must redirect to the
        provider payment page and call confirm_subscription() on webhook.
        """
        idempotency_key = f"sub-{user.id}-{plan.id}-{uuid.uuid4().hex[:8]}"

        subscription = Subscription.objects.create(
            user=user,
            plan=plan,
            provider=provider,
            status=PaymentStatus.PENDING,
        )

        sub_ct = ContentType.objects.get_for_model(Subscription)
        payment_txn = PaymentTransaction.objects.create(
            provider=provider,
            kind="subscription",
            amount=plan.price,
            currency=plan.currency,
            status=PaymentStatus.PENDING,
            content_type=sub_ct,
            object_id=str(subscription.id),
            idempotency_key=idempotency_key,
        )

        logger.info(
            "Initiated subscription %s for user %s (plan: %s, provider: %s)",
            subscription.id,
            user.id,
            plan.name,
            provider,
        )
        return subscription, payment_txn

    @staticmethod
    @transaction.atomic
    def confirm_subscription(
        subscription: Subscription,
        payment_txn: PaymentTransaction,
        provider_subscription_id: str = "",
        provider_payment_id: str = "",
        raw: dict | None = None,
    ) -> Subscription:
        """
        Mark subscription and transaction as succeeded.
        Call this from a webhook handler or after provider confirms payment.
        """
        now = timezone.now()
        plan = subscription.plan

        # Determine period end based on plan interval
        if plan.interval == "year":
            from dateutil.relativedelta import relativedelta
            period_end = now + relativedelta(years=1)
        elif plan.interval == "week":
            from datetime import timedelta
            period_end = now + timedelta(weeks=1)
        else:
            # Default: monthly
            from dateutil.relativedelta import relativedelta
            period_end = now + relativedelta(months=1)

        subscription.status = PaymentStatus.SUCCEEDED
        subscription.provider_subscription_id = provider_subscription_id
        subscription.current_period_start = now
        subscription.current_period_end = period_end
        subscription.save(
            update_fields=[
                "status",
                "provider_subscription_id",
                "current_period_start",
                "current_period_end",
                "updated_at",
            ]
        )

        payment_txn.mark_succeeded(provider_payment_id=provider_payment_id, raw=raw)

        logger.info("Confirmed subscription %s for user %s", subscription.id, subscription.user_id)
        return subscription

    @staticmethod
    @transaction.atomic
    def cancel_subscription(subscription: Subscription, at_period_end: bool = True) -> Subscription:
        """
        Cancel a subscription.
        If at_period_end=True, mark cancel_at_period_end and keep active until period expires.
        If at_period_end=False, immediately mark as cancelled.
        Free subscriptions are cancelled immediately (no period end concept).
        """
        if subscription.status == PaymentStatus.FREE_ACCEPTED:
            subscription.status = PaymentStatus.CANCELLED
            subscription.cancel_at_period_end = False
            subscription.save(update_fields=["status", "cancel_at_period_end", "updated_at"])
        elif at_period_end:
            subscription.cancel_at_period_end = True
            subscription.save(update_fields=["cancel_at_period_end", "updated_at"])
        else:
            subscription.status = PaymentStatus.CANCELLED
            subscription.cancel_at_period_end = False
            subscription.save(update_fields=["status", "cancel_at_period_end", "updated_at"])

        logger.info(
            "Cancelled subscription %s (at_period_end=%s) for user %s",
            subscription.id,
            at_period_end,
            subscription.user_id,
        )
        return subscription

    @staticmethod
    @transaction.atomic
    def change_plan(user, new_plan: Plan, provider: str, current_subscription: Subscription | None = None) -> tuple[Subscription, PaymentTransaction] | Subscription:
        """
        Change a user's subscription to a different plan.
        Optionally cancels the current subscription at period end.
        For free plans, activates immediately and returns a Subscription (no PaymentTransaction).
        For paid plans, creates a new Subscription + PaymentTransaction in pending state.
        """
        if current_subscription and current_subscription.status in [PaymentStatus.SUCCEEDED, PaymentStatus.FREE_ACCEPTED]:
            SubscriptionService.cancel_subscription(current_subscription, at_period_end=True)

        if new_plan.price == Decimal("0.00") or new_plan.price == 0:
            return SubscriptionService.subscribe_free(user, new_plan)
        return SubscriptionService.initiate_subscription(user, new_plan, provider)

