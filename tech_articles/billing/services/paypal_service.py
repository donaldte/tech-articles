"""
PayPal payment service.
Uses PayPal REST API v2 for subscription billing.
"""
from __future__ import annotations

import logging

import requests
from django.conf import settings
from django.urls import reverse

from tech_articles.billing.models import Plan, Subscription, PaymentTransaction

logger = logging.getLogger(__name__)


class PayPalService:
    """
    PayPal payment service.
    Uses PayPal REST API v2 (subscriptions).
    """

    @staticmethod
    def _get_access_token() -> str:
        """Obtain a PayPal OAuth2 access token."""
        url = f"{settings.PAYPAL_API_BASE_URL}/v1/oauth2/token"
        response = requests.post(
            url,
            auth=(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_CLIENT_SECRET),
            data={"grant_type": "client_credentials"},
            timeout=15,
        )
        response.raise_for_status()
        return response.json()["access_token"]

    @staticmethod
    def _headers(token: str) -> dict:
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    @staticmethod
    def create_subscription(
        subscription,
        payment_txn: PaymentTransaction,
        request,
    ) -> str:
        """
        Create a PayPal subscription and return the approval URL to redirect the user.
        The plan must have a valid `provider_price_id` (PayPal billing plan ID).
        """
        plan: Plan = subscription.plan
        token = PayPalService._get_access_token()

        return_url = request.build_absolute_uri(
            reverse("billing:paypal_return")
        ) + f"?subscription_id={subscription.id}&txn_id={payment_txn.id}"
        cancel_url = request.build_absolute_uri(
            reverse("billing:subscribe", kwargs={"slug": plan.slug})
        )

        body = {
            "plan_id": plan.provider_price_id,  # PayPal Billing Plan ID
            "quantity": "1",
            "auto_renewal": True,
            "application_context": {
                "brand_name": getattr(settings, "PAYPAL_BRAND_NAME", "Runbookly"),
                "locale": "en-US",
                "shipping_preference": "NO_SHIPPING",
                "user_action": "SUBSCRIBE_NOW",
                "return_url": return_url,
                "cancel_url": cancel_url,
            },
            "custom_id": str(subscription.id),
        }

        response = requests.post(
            f"{settings.PAYPAL_API_BASE_URL}/v1/billing/subscriptions",
            json=body,
            headers=PayPalService._headers(token),
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()

        paypal_sub_id = data.get("id", "")
        payment_txn.provider_subscription_id = paypal_sub_id
        payment_txn.save(update_fields=["provider_subscription_id", "updated_at"])

        # Extract the approval link
        approval_url = next(
            (link["href"] for link in data.get("links", []) if link.get("rel") == "approve"),
            None,
        )
        if not approval_url:
            raise ValueError("PayPal did not return an approval URL.")

        logger.info(
            "Created PayPal subscription %s for subscription %s",
            paypal_sub_id,
            subscription.id,
        )
        return approval_url

    @staticmethod
    def get_subscription_details(paypal_subscription_id: str) -> dict:
        """Retrieve PayPal subscription details."""
        token = PayPalService._get_access_token()
        response = requests.get(
            f"{settings.PAYPAL_API_BASE_URL}/v1/billing/subscriptions/{paypal_subscription_id}",
            headers=PayPalService._headers(token),
            timeout=15,
        )
        response.raise_for_status()
        return response.json()

    @staticmethod
    def cancel_subscription(paypal_subscription_id: str, reason: str = "User requested cancellation") -> None:
        """Cancel a PayPal subscription."""
        token = PayPalService._get_access_token()
        response = requests.post(
            f"{settings.PAYPAL_API_BASE_URL}/v1/billing/subscriptions/{paypal_subscription_id}/cancel",
            json={"reason": reason},
            headers=PayPalService._headers(token),
            timeout=15,
        )
        if response.status_code != 204:
            response.raise_for_status()
        logger.info("Cancelled PayPal subscription %s", paypal_subscription_id)

    @staticmethod
    def verify_webhook_signature(
        transmission_id: str,
        timestamp: str,
        webhook_id: str,
        event_body: str,
        cert_url: str,
        actual_signature: str,
        auth_algo: str,
    ) -> bool:
        """Verify the authenticity of a PayPal webhook event."""
        token = PayPalService._get_access_token()
        body = {
            "transmission_id": transmission_id,
            "transmission_time": timestamp,
            "cert_url": cert_url,
            "auth_algo": auth_algo,
            "transmission_sig": actual_signature,
            "webhook_id": webhook_id,
            "webhook_event": event_body,
        }
        response = requests.post(
            f"{settings.PAYPAL_API_BASE_URL}/v1/notifications/verify-webhook-signature",
            json=body,
            headers=PayPalService._headers(token),
            timeout=15,
        )
        if response.status_code != 200:
            return False
        return response.json().get("verification_status") == "SUCCESS"
