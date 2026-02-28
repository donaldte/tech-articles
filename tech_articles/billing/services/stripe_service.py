"""
Stripe payment service.
Handles Stripe Checkout sessions for subscriptions (card, Apple Pay, Google Pay, SEPA).
"""

from __future__ import annotations

import logging

import stripe
from django.conf import settings
from django.urls import reverse

from tech_articles.billing.models import Purchase, Subscription, PaymentTransaction

logger = logging.getLogger(__name__)


def _get_stripe_client() -> stripe.StripeClient:
    """Return a configured Stripe client."""
    return stripe.StripeClient(settings.STRIPE_SECRET_KEY)


class StripeService:
    """
    Stripe payment service for subscription checkout.
    Supports: card, Apple Pay, Google Pay, SEPA Direct Debit.

    Apple Pay and Google Pay are wallet methods automatically enabled by Stripe when
    the card payment method is active and the browser/device supports them.
    SEPA Direct Debit is enabled explicitly for EUR subscriptions.
    """

    # Payment methods for EUR-based subscriptions (adds SEPA)
    EUR_PAYMENT_METHOD_TYPES = ["card", "sepa_debit"]
    # Payment methods for all other currencies (card includes Apple Pay / Google Pay via Stripe)
    DEFAULT_PAYMENT_METHOD_TYPES = ["card"]

    @staticmethod
    def create_checkout_session(
        subscription: Subscription,
        payment_txn: PaymentTransaction,
        request,
    ) -> str:
        """
        Create a Stripe Checkout session for a subscription.
        - card: Stripe automatically enables Apple Pay and Google Pay on supported browsers/devices.
        - sepa_debit: enabled for EUR subscriptions.
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

        # Enable SEPA for EUR subscriptions; card always includes Apple Pay + Google Pay
        currency = plan.currency.lower()
        payment_method_types = (
            StripeService.EUR_PAYMENT_METHOD_TYPES
            if currency == "eur"
            else StripeService.DEFAULT_PAYMENT_METHOD_TYPES
        )

        session_params = {
            "mode": "subscription",
            "payment_method_types": payment_method_types,
            "success_url": success_url,
            "cancel_url": cancel_url,
            "metadata": {
                "subscription_id": str(subscription.id),
                "payment_txn_id": str(payment_txn.id),
                "plan_id": str(plan.id),
            },
            "client_reference_id": str(subscription.user_id),
        }

        # Use pre-configured Stripe price if available; otherwise create inline price data
        if plan.provider_price_id:
            session_params["line_items"] = [{"price": plan.provider_price_id, "quantity": 1}]
        else:
            session_params["line_items"] = [
                {
                    "price_data": {
                        "currency": currency,
                        "unit_amount": int(plan.price * 100),  # Stripe expects cents
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
            "Created Stripe Checkout session %s for subscription %s (methods: %s)",
            session.id,
            subscription.id,
            payment_method_types,
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

    @staticmethod
    def create_appointment_checkout_session(
        appointment,
        payment_txn: PaymentTransaction,
        request,
    ) -> str:
        """
        Create a Stripe Checkout session for a one-time appointment payment.
        Supports card, Apple Pay, Google Pay automatically.
        Returns the URL to redirect the user to.
        """
        client = _get_stripe_client()

        success_url = (
            request.build_absolute_uri(
                reverse(
                    "billing:appointment_payment_success",
                    kwargs={"transaction_id": payment_txn.id},
                )
            )
            + "?session_id={CHECKOUT_SESSION_ID}"
        )
        cancel_url = request.build_absolute_uri(
            reverse(
                "billing:appointment_payment_summary",
                kwargs={"transaction_id": payment_txn.id},
            )
        )

        currency = (appointment.currency or "USD").lower()
        payment_method_types = (
            ["card", "sepa_debit"] if currency == "eur" else ["card"]
        )

        appointment_type_name = (
            appointment.appointment_type.name
            if appointment.appointment_type
            else "Appointment"
        )

        session_params = {
            "mode": "payment",
            "payment_method_types": payment_method_types,
            "success_url": success_url,
            "cancel_url": cancel_url,
            "metadata": {
                "appointment_id": str(appointment.id),
                "payment_txn_id": str(payment_txn.id),
            },
            "client_reference_id": str(appointment.user_id),
            "line_items": [
                {
                    "price_data": {
                        "currency": currency,
                        "unit_amount": int(appointment.total_amount * 100),
                        "product_data": {"name": appointment_type_name},
                    },
                    "quantity": 1,
                }
            ],
        }

        session = client.checkout.sessions.create(session_params)

        payment_txn.provider_payment_id = session.id
        payment_txn.save(update_fields=["provider_payment_id", "updated_at"])

        logger.info(
            "Created Stripe appointment checkout session %s for appointment %s",
            session.id,
            appointment.id,
        )
        return session.url

    @staticmethod
    def create_purchase_checkout_session(
        purchase: Purchase,
        payment_txn: PaymentTransaction,
        request,
    ) -> str:
        """
        Create a Stripe Checkout session for a one-time article purchase.
        Supports card, Apple Pay, Google Pay automatically.
        Returns the URL to redirect the user to.
        """
        client = _get_stripe_client()
        article = purchase.article

        success_url = (
            request.build_absolute_uri(reverse("billing:purchase_stripe_success"))
            + "?session_id={CHECKOUT_SESSION_ID}"
        )
        cancel_url = request.build_absolute_uri(
            reverse("billing:purchase_cancel", kwargs={"pk": purchase.id})
        )

        currency = (article.currency or "USD").lower()
        # card includes Apple Pay + Google Pay on supported browsers/devices
        payment_method_types = (
            ["card", "sepa_debit"] if currency == "eur" else ["card"]
        )

        session_params = {
            "mode": "payment",
            "payment_method_types": payment_method_types,
            "success_url": success_url,
            "cancel_url": cancel_url,
            "metadata": {
                "purchase_id": str(purchase.id),
                "payment_txn_id": str(payment_txn.id),
                "article_id": str(article.id),
            },
            "client_reference_id": str(purchase.user_id),
            "line_items": [
                {
                    "price_data": {
                        "currency": currency,
                        "unit_amount": int(article.price * 100),
                        "product_data": {"name": article.title},
                    },
                    "quantity": 1,
                }
            ],
        }

        session = client.checkout.sessions.create(session_params)

        payment_txn.provider_payment_id = session.id
        payment_txn.save(update_fields=["provider_payment_id", "updated_at"])

        logger.info(
            "Created Stripe purchase checkout session %s for purchase %s (article: %s)",
            session.id,
            purchase.id,
            article.id,
        )
        return session.url
