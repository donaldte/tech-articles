"""
Webhook views for Stripe and PayPal.
These endpoints receive payment events and update subscription/transaction records.
"""
from __future__ import annotations

import json
import logging

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from tech_articles.billing.models import Subscription, PaymentTransaction
from tech_articles.billing.services import SubscriptionService, StripeService
from tech_articles.utils.enums import PaymentStatus

logger = logging.getLogger(__name__)


# ============================================================================
# Stripe Webhook
# ============================================================================

@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(View):
    """
    Handle Stripe webhook events.
    Stripe docs: https://docs.stripe.com/webhooks
    """

    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

        if not sig_header:
            return HttpResponseBadRequest("Missing Stripe-Signature header.")

        if not settings.STRIPE_WEBHOOK_SECRET:
            logger.warning("STRIPE_WEBHOOK_SECRET not set — skipping signature verification.")
            try:
                event = json.loads(payload)
            except json.JSONDecodeError:
                return HttpResponseBadRequest("Invalid JSON.")
        else:
            try:
                event = StripeService.construct_webhook_event(payload, sig_header)
            except Exception as exc:
                logger.warning("Stripe webhook signature verification failed: %s", exc)
                return HttpResponse(status=400)

        event_type = event.get("type") if isinstance(event, dict) else event.type
        logger.info("Stripe webhook received: %s", event_type)

        handlers = {
            "checkout.session.completed": _handle_stripe_checkout_completed,
            "customer.subscription.deleted": _handle_stripe_subscription_deleted,
            "invoice.payment_failed": _handle_stripe_invoice_payment_failed,
        }

        handler = handlers.get(event_type)
        if handler:
            try:
                handler(event)
            except Exception as exc:
                logger.exception("Error handling Stripe event %s: %s", event_type, exc)
                return HttpResponse(status=500)

        return HttpResponse(status=200)


def _handle_stripe_checkout_completed(event):
    """Handle checkout.session.completed — activate subscription."""
    data = event["data"]["object"] if isinstance(event, dict) else event.data.object
    metadata = data.get("metadata", {})
    subscription_id = metadata.get("subscription_id")
    txn_id = metadata.get("payment_txn_id")

    if not subscription_id or not txn_id:
        logger.warning("Stripe checkout.session.completed missing metadata: %s", metadata)
        return

    try:
        subscription = Subscription.objects.get(id=subscription_id)
        payment_txn = PaymentTransaction.objects.get(id=txn_id)

        if payment_txn.webhook_processed:
            logger.info("Stripe event already processed for txn %s", txn_id)
            return

        stripe_subscription_id = data.get("subscription", "")
        SubscriptionService.confirm_subscription(
            subscription=subscription,
            payment_txn=payment_txn,
            provider_subscription_id=stripe_subscription_id,
            provider_payment_id=data.get("id", ""),
            raw=data if isinstance(data, dict) else dict(data),
        )
        payment_txn.webhook_processed = True
        payment_txn.save(update_fields=["webhook_processed", "updated_at"])
        logger.info("Activated subscription %s via Stripe webhook", subscription_id)
    except (Subscription.DoesNotExist, PaymentTransaction.DoesNotExist) as exc:
        logger.error("Stripe checkout webhook: object not found: %s", exc)


def _handle_stripe_subscription_deleted(event):
    """Handle customer.subscription.deleted — cancel subscription."""
    data = event["data"]["object"] if isinstance(event, dict) else event.data.object
    stripe_sub_id = data.get("id", "")

    subscription = Subscription.objects.filter(
        provider_subscription_id=stripe_sub_id
    ).first()
    if subscription:
        SubscriptionService.cancel_subscription(subscription, at_period_end=False)
        logger.info("Cancelled subscription %s via Stripe webhook", subscription.id)


def _handle_stripe_invoice_payment_failed(event):
    """Handle invoice.payment_failed — mark transaction as failed."""
    data = event["data"]["object"] if isinstance(event, dict) else event.data.object
    stripe_sub_id = data.get("subscription", "")

    sub_ct = ContentType.objects.get_for_model(Subscription)
    subscription = Subscription.objects.filter(
        provider_subscription_id=stripe_sub_id
    ).first()
    if subscription:
        txn = PaymentTransaction.objects.filter(
            content_type=sub_ct,
            object_id=str(subscription.id),
            status=PaymentStatus.PENDING,
        ).first()
        if txn:
            txn.mark_failed(
                error_message=data.get("last_finalization_error", {}).get("message", "Payment failed"),
                raw=data if isinstance(data, dict) else dict(data),
            )
            logger.info("Marked transaction %s as failed via Stripe webhook", txn.id)


# ============================================================================
# PayPal Webhook
# ============================================================================

@method_decorator(csrf_exempt, name="dispatch")
class PayPalWebhookView(View):
    """
    Handle PayPal webhook events.
    PayPal docs: https://developer.paypal.com/api/rest/webhooks/
    """

    def post(self, request, *args, **kwargs):
        try:
            event = json.loads(request.body)
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON.")

        # Verify signature if webhook ID is configured
        if settings.PAYPAL_WEBHOOK_ID:
            from tech_articles.billing.services import PayPalService
            verified = PayPalService.verify_webhook_signature(
                transmission_id=request.META.get("HTTP_PAYPAL_TRANSMISSION_ID", ""),
                timestamp=request.META.get("HTTP_PAYPAL_TRANSMISSION_TIME", ""),
                webhook_id=settings.PAYPAL_WEBHOOK_ID,
                event_body=event,
                cert_url=request.META.get("HTTP_PAYPAL_CERT_URL", ""),
                actual_signature=request.META.get("HTTP_PAYPAL_TRANSMISSION_SIG", ""),
                auth_algo=request.META.get("HTTP_PAYPAL_AUTH_ALGO", ""),
            )
            if not verified:
                logger.warning("PayPal webhook signature verification failed.")
                return HttpResponse(status=400)

        event_type = event.get("event_type", "")
        logger.info("PayPal webhook received: %s", event_type)

        handlers = {
            "BILLING.SUBSCRIPTION.ACTIVATED": _handle_paypal_subscription_activated,
            "BILLING.SUBSCRIPTION.CANCELLED": _handle_paypal_subscription_cancelled,
            "PAYMENT.SALE.COMPLETED": _handle_paypal_payment_completed,
        }

        handler = handlers.get(event_type)
        if handler:
            try:
                handler(event)
            except Exception as exc:
                logger.exception("Error handling PayPal event %s: %s", event_type, exc)
                return HttpResponse(status=500)

        return HttpResponse(status=200)


def _handle_paypal_subscription_activated(event):
    """Handle BILLING.SUBSCRIPTION.ACTIVATED — activate subscription."""
    resource = event.get("resource", {})
    paypal_sub_id = resource.get("id", "")
    custom_id = resource.get("custom_id", "")  # our subscription.id stored in custom_id

    if not custom_id:
        logger.warning("PayPal subscription activated without custom_id")
        return

    try:
        subscription = Subscription.objects.get(id=custom_id)
        sub_ct = ContentType.objects.get_for_model(Subscription)
        payment_txn = PaymentTransaction.objects.filter(
            content_type=sub_ct,
            object_id=str(subscription.id),
            status=PaymentStatus.PENDING,
        ).first()

        if payment_txn and not payment_txn.webhook_processed:
            SubscriptionService.confirm_subscription(
                subscription=subscription,
                payment_txn=payment_txn,
                provider_subscription_id=paypal_sub_id,
                raw=resource,
            )
            payment_txn.webhook_processed = True
            payment_txn.save(update_fields=["webhook_processed", "updated_at"])
            logger.info("Activated subscription %s via PayPal webhook", custom_id)
    except Subscription.DoesNotExist:
        logger.error("PayPal webhook: subscription %s not found", custom_id)


def _handle_paypal_subscription_cancelled(event):
    """Handle BILLING.SUBSCRIPTION.CANCELLED — cancel subscription."""
    resource = event.get("resource", {})
    paypal_sub_id = resource.get("id", "")

    subscription = Subscription.objects.filter(
        provider_subscription_id=paypal_sub_id
    ).first()
    if subscription:
        SubscriptionService.cancel_subscription(subscription, at_period_end=False)
        logger.info("Cancelled subscription %s via PayPal webhook", subscription.id)


def _handle_paypal_payment_completed(event):
    """Handle PAYMENT.SALE.COMPLETED — log a successful recurring payment."""
    resource = event.get("resource", {})
    billing_agreement_id = resource.get("billing_agreement_id", "")

    if billing_agreement_id:
        subscription = Subscription.objects.filter(
            provider_subscription_id=billing_agreement_id
        ).first()
        if subscription:
            logger.info(
                "PayPal recurring payment completed for subscription %s",
                subscription.id,
            )
