"""
Stripe payment service.
Handles Stripe Checkout sessions for subscriptions (card, Apple Pay, Google Pay, SEPA).
"""

from __future__ import annotations

import logging

import stripe
from django.conf import settings
from django.urls import reverse

from tech_articles.billing.models import Subscription, PaymentTransaction

logger = logging.getLogger(__name__)


def _get_stripe_client() -> stripe.StripeClient:
    """Return a configured Stripe client."""
    return stripe.StripeClient(settings.STRIPE_SECRET_KEY)


class StripeService:
    """
    Stripe payment service for subscription checkout.
    Supports: card, Apple Pay, Google Pay, SEPA Direct Debit.
    """

    # Payment methods enabled on Checkout sessions
    PAYMENT_METHOD_TYPES = ["card", "sepa_debit"]

    @staticmethod
    def create_checkout_session(
        subscription: Subscription,
        payment_txn: PaymentTransaction,
        request,
    ) -> str:
        """
        Create a Stripe Checkout session for a subscription.
        Returns the URL to redirect the user to.
        """
        client = _get_stripe_client()
        plan = subscription.plan

        # Build absolute success / cancel URLs
        success_url = (
            request.build_absolute_uri(reverse("billing:stripe_success"))
            + "?session_id={CHECKOUT_SESSION_ID}"
        )
        cancel_url = request.build_absolute_uri(
            reverse("billing:subscribe", kwargs={"slug": plan.slug})
        )

        # Map plan interval to Stripe interval
        interval_map = {
            "month": "month",
            "year": "year",
            "week": "week",
        }
        stripe_interval = interval_map.get(plan.interval, "month")

        # Create or retrieve Stripe price (use provider_price_id if set)
        if plan.provider_price_id:
            price_id = plan.provider_price_id
        else:
            # Create an inline price if no Stripe price ID configured
            price_id = None

        session_params = {
            "mode": "subscription",
            "payment_method_types": StripeService.PAYMENT_METHOD_TYPES,
            "success_url": success_url,
            "cancel_url": cancel_url,
            "metadata": {
                "subscription_id": str(subscription.id),
                "payment_txn_id": str(payment_txn.id),
                "plan_id": str(plan.id),
            },
            "client_reference_id": str(subscription.user_id),
        }

        if price_id:
            session_params["line_items"] = [{"price": price_id, "quantity": 1}]
        else:
            # Create inline price data
            session_params["line_items"] = [
                {
                    "price_data": {
                        "currency": plan.currency.lower(),
                        "unit_amount": int(plan.price * 100),  # cents
                        "recurring": {"interval": stripe_interval},
                        "product_data": {"name": plan.name},
                    },
                    "quantity": 1,
                }
            ]

        session = client.checkout.sessions.create(session_params)

        # Store the session ID on the transaction for later retrieval
        payment_txn.provider_payment_id = session.id
        payment_txn.save(update_fields=["provider_payment_id", "updated_at"])

        logger.info(
            "Created Stripe Checkout session %s for subscription %s",
            session.id,
            subscription.id,
        )
        return session.url

    @staticmethod
    def retrieve_checkout_session(session_id: str) -> dict:
        """Retrieve a Stripe Checkout session by ID."""
        client = _get_stripe_client()
        return client.checkout.sessions.retrieve(session_id)

    @staticmethod
    def construct_webhook_event(payload: bytes, sig_header: str) -> stripe.Event:
        """Construct and verify a Stripe webhook event."""
        return stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )

    @staticmethod
    def cancel_stripe_subscription(
        provider_subscription_id: str, at_period_end: bool = True
    ) -> None:
        """Cancel a Stripe subscription via API."""
        client = _get_stripe_client()
        if at_period_end:
            client.subscriptions.update(
                provider_subscription_id,
                {"cancel_at_period_end": True},
            )
        else:
            client.subscriptions.cancel(provider_subscription_id)
        logger.info(
            "Cancelled Stripe subscription %s (at_period_end=%s)",
            provider_subscription_id,
            at_period_end,
        )
