"""
PayPal payment service.
Uses PayPal REST API v2 for subscription billing.
"""

from __future__ import annotations

import logging

import requests
from django.conf import settings
from django.urls import reverse

from tech_articles.billing.models import Plan, PaymentTransaction

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
    def _ensure_paypal_plan_id(plan: Plan, token: str) -> str:
        """
        Return the PayPal billing plan ID for a given Plan.
        If plan.provider_price_id is not set, creates a product + billing plan
        in PayPal and saves the ID back to the plan for reuse.
        """
        if plan.provider_price_id:
            return plan.provider_price_id

        headers = PayPalService._headers(token)
        base_url = settings.PAYPAL_API_BASE_URL

        # 1. Create a PayPal product
        product_resp = requests.post(
            f"{base_url}/v1/catalogs/products",
            json={
                "name": plan.name,
                "type": "SERVICE",
                "category": "SOFTWARE",
            },
            headers=headers,
            timeout=15,
        )
        product_resp.raise_for_status()
        product_id = product_resp.json()["id"]

        # 2. Map interval to PayPal format
        interval_map = {
            "week": ("WEEK", 1),
            "month": ("MONTH", 1),
            "year": ("YEAR", 1),
        }
        paypal_interval, interval_count = interval_map.get(plan.interval, ("MONTH", 1))

        # 3. Build billing cycles list (trial first if configured, then regular)
        billing_cycles = []
        sequence = 1

        if plan.trial_period_days:
            billing_cycles.append({
                "frequency": {"interval_unit": "DAY", "interval_count": plan.trial_period_days},
                "tenure_type": "TRIAL",
                "sequence": sequence,
                "total_cycles": 1,
                "pricing_scheme": {
                    "fixed_price": {"value": "0", "currency_code": plan.currency.upper()}
                },
            })
            sequence += 1

        billing_cycles.append({
            "frequency": {
                "interval_unit": paypal_interval,
                "interval_count": interval_count,
            },
            "tenure_type": "REGULAR",
            "sequence": sequence,
            "total_cycles": 0,  # 0 = infinite
            "pricing_scheme": {
                "fixed_price": {
                    "value": str(plan.price),
                    "currency_code": plan.currency.upper(),
                }
            },
        })

        # 4. Create the PayPal billing plan
        plan_body = {
            "product_id": product_id,
            "name": plan.name,
            "billing_cycles": billing_cycles,
            "payment_preferences": {
                "auto_bill_outstanding": True,
                "payment_failure_threshold": 3,
            },
        }

        plan_resp = requests.post(
            f"{base_url}/v1/billing/plans",
            json=plan_body,
            headers=headers,
            timeout=15,
        )
        plan_resp.raise_for_status()
        paypal_plan_id = plan_resp.json()["id"]

        # Save back to our Plan model to avoid re-creating on future calls
        Plan.objects.filter(pk=plan.pk).update(provider_price_id=paypal_plan_id)
        plan.provider_price_id = paypal_plan_id  # update in-memory too

        logger.info("Created PayPal billing plan %s for plan '%s'", paypal_plan_id, plan.name)
        return paypal_plan_id

    @staticmethod
    def create_subscription(
        subscription,
        payment_txn: PaymentTransaction,
        request,
    ) -> str:
        """
        Create a PayPal subscription and return the approval URL to redirect the user.
        Automatically creates a PayPal billing plan if plan.provider_price_id is not set.
        """
        plan: Plan = subscription.plan
        token = PayPalService._get_access_token()

        # Ensure we have a valid PayPal plan ID (create product + plan in PayPal if missing)
        paypal_plan_id = PayPalService._ensure_paypal_plan_id(plan, token)

        return_url = (
            request.build_absolute_uri(reverse("billing:paypal_return"))
            + f"?subscription_id={subscription.id}&txn_id={payment_txn.id}"
        )
        cancel_url = request.build_absolute_uri(
            reverse("billing:subscribe", kwargs={"slug": plan.slug})
        )

        body = {
            "plan_id": paypal_plan_id,
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
            (
                link["href"]
                for link in data.get("links", [])
                if link.get("rel") == "approve"
            ),
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
    def cancel_subscription(
        paypal_subscription_id: str, reason: str = "User requested cancellation"
    ) -> None:
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

    @staticmethod
    def create_purchase_order(
        purchase,
        payment_txn,
        request,
    ) -> str:
        """
        Create a PayPal order for a one-time article purchase.
        Returns the approval URL to redirect the user to.
        """
        from django.urls import reverse

        article = purchase.article
        token = PayPalService._get_access_token()

        return_url = (
            request.build_absolute_uri(reverse("billing:purchase_paypal_return"))
            + f"?purchase_id={purchase.id}&txn_id={payment_txn.id}"
        )
        cancel_url = request.build_absolute_uri(
            reverse("billing:purchase_cancel", kwargs={"pk": purchase.id})
        )

        body = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "amount": {
                        "currency_code": (article.currency or "USD").upper(),
                        "value": str(article.price),
                    },
                    "description": article.title[:127],
                    "custom_id": str(purchase.id),
                }
            ],
            "application_context": {
                "brand_name": getattr(settings, "PAYPAL_BRAND_NAME", "Runbookly"),
                "locale": "en-US",
                "shipping_preference": "NO_SHIPPING",
                "user_action": "PAY_NOW",
                "return_url": return_url,
                "cancel_url": cancel_url,
            },
        }

        response = requests.post(
            f"{settings.PAYPAL_API_BASE_URL}/v2/checkout/orders",
            json=body,
            headers=PayPalService._headers(token),
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()

        paypal_order_id = data.get("id", "")
        payment_txn.provider_payment_id = paypal_order_id
        payment_txn.save(update_fields=["provider_payment_id", "updated_at"])

        approval_url = next(
            (
                link["href"]
                for link in data.get("links", [])
                if link.get("rel") == "approve"
            ),
            None,
        )
        if not approval_url:
            raise ValueError("PayPal did not return an approval URL.")

        logger.info(
            "Created PayPal order %s for purchase %s (article: %s)",
            paypal_order_id,
            purchase.id,
            article.id,
        )
        return approval_url

    @staticmethod
    def capture_order(paypal_order_id: str) -> dict:
        """Capture a PayPal order (complete the payment)."""
        token = PayPalService._get_access_token()
        response = requests.post(
            f"{settings.PAYPAL_API_BASE_URL}/v2/checkout/orders/{paypal_order_id}/capture",
            json={},
            headers=PayPalService._headers(token),
            timeout=15,
        )
        response.raise_for_status()
        return response.json()
