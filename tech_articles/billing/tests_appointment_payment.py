"""
Tests for appointment payment flows:
- AppointmentPaymentService
- AppointmentPaymentCreateView
- Stripe / PayPal webhook handlers for appointment payments
- Idempotency and subscription flow isolation
"""
from __future__ import annotations

import json
import uuid
from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from tech_articles.appointments.models import (
    Appointment,
    AppointmentSlot,
    AppointmentType,
)
from tech_articles.billing.models import PaymentTransaction, Plan, Subscription
from tech_articles.billing.services import AppointmentPaymentService
from tech_articles.utils.enums import (
    AppointmentStatus,
    PaymentProvider,
    PaymentStatus,
    PlanInterval,
    CurrencyChoices,
)

User = get_user_model()


# ============================================================================
# Helpers
# ============================================================================


def _make_user(**kwargs):
    defaults = {"email": f"user-{uuid.uuid4().hex[:6]}@example.com", "password": "pass"}
    defaults.update(kwargs)
    return User.objects.create_user(**defaults)


def _make_appointment(user, amount="50.00", currency="USD"):
    appt_type = AppointmentType.objects.create(
        name=f"Type-{uuid.uuid4().hex[:4]}",
        base_hourly_rate=Decimal("50.00"),
        currency=currency,
    )
    slot = AppointmentSlot.objects.create(
        start_at=timezone.now() + timezone.timedelta(days=1),
        end_at=timezone.now() + timezone.timedelta(days=1, hours=1),
    )
    return Appointment.objects.create(
        user=user,
        slot=slot,
        appointment_type=appt_type,
        duration_minutes=60,
        hourly_rate=Decimal("50.00"),
        total_amount=Decimal(amount),
        currency=currency,
        status=AppointmentStatus.PENDING,
        payment_status=PaymentStatus.PENDING,
    )


# ============================================================================
# AppointmentPaymentService
# ============================================================================


class AppointmentPaymentServiceTestCase(TestCase):
    def setUp(self):
        self.user = _make_user()
        self.appointment = _make_appointment(self.user)

    def test_initiate_payment_creates_transaction(self):
        """initiate_payment should create a PENDING PaymentTransaction linked to the appointment."""
        txn = AppointmentPaymentService.initiate_payment(
            appointment=self.appointment,
            provider=PaymentProvider.STRIPE,
        )
        self.assertIsNotNone(txn.id)
        self.assertEqual(txn.status, PaymentStatus.PENDING)
        self.assertEqual(txn.appointment, self.appointment)
        self.assertEqual(txn.amount, self.appointment.total_amount)
        self.assertEqual(txn.kind, "appointment")

    def test_initiate_payment_raises_if_already_paid(self):
        """initiate_payment should raise ValueError if appointment already paid."""
        self.appointment.payment_status = PaymentStatus.SUCCEEDED
        self.appointment.save()
        with self.assertRaises(ValueError):
            AppointmentPaymentService.initiate_payment(
                appointment=self.appointment,
                provider=PaymentProvider.STRIPE,
            )

    def test_confirm_payment_sets_succeeded_and_confirms_appointment(self):
        """confirm_payment should mark transaction as succeeded and confirm the appointment."""
        txn = AppointmentPaymentService.initiate_payment(
            appointment=self.appointment,
            provider=PaymentProvider.STRIPE,
        )
        AppointmentPaymentService.confirm_payment(
            payment_txn=txn,
            provider_payment_id="pi_test_123",
        )

        txn.refresh_from_db()
        self.appointment.refresh_from_db()

        self.assertEqual(txn.status, PaymentStatus.SUCCEEDED)
        self.assertEqual(txn.provider_payment_id, "pi_test_123")
        self.assertEqual(self.appointment.payment_status, PaymentStatus.SUCCEEDED)
        self.assertEqual(self.appointment.status, AppointmentStatus.CONFIRMED)
        self.assertIsNotNone(self.appointment.confirmed_at)

    def test_confirm_payment_is_idempotent(self):
        """Calling confirm_payment twice should not raise and should not change status."""
        txn = AppointmentPaymentService.initiate_payment(
            appointment=self.appointment,
            provider=PaymentProvider.STRIPE,
        )
        AppointmentPaymentService.confirm_payment(payment_txn=txn, provider_payment_id="pi_1")
        AppointmentPaymentService.confirm_payment(payment_txn=txn, provider_payment_id="pi_1")

        txn.refresh_from_db()
        self.assertEqual(txn.status, PaymentStatus.SUCCEEDED)

    def test_fail_payment_marks_transaction_failed_and_leaves_appointment_unconfirmed(self):
        """fail_payment should mark transaction as failed; appointment stays unconfirmed."""
        txn = AppointmentPaymentService.initiate_payment(
            appointment=self.appointment,
            provider=PaymentProvider.STRIPE,
        )
        AppointmentPaymentService.fail_payment(txn, error_message="card declined")

        txn.refresh_from_db()
        self.appointment.refresh_from_db()

        self.assertEqual(txn.status, PaymentStatus.FAILED)
        self.assertNotEqual(self.appointment.status, AppointmentStatus.CONFIRMED)
        self.assertIsNone(self.appointment.confirmed_at)

    def test_amount_matches_validates_correctly(self):
        """amount_matches should return True when amount and currency match."""
        txn = AppointmentPaymentService.initiate_payment(
            appointment=self.appointment,
            provider=PaymentProvider.STRIPE,
        )
        # 50.00 USD => 5000 cents
        self.assertTrue(AppointmentPaymentService.amount_matches(txn, 5000, "USD"))
        self.assertFalse(AppointmentPaymentService.amount_matches(txn, 4999, "USD"))
        self.assertFalse(AppointmentPaymentService.amount_matches(txn, 5000, "EUR"))

    def test_has_paid_returns_false_before_payment(self):
        """has_paid should return False if no succeeded transaction exists."""
        self.assertFalse(AppointmentPaymentService.has_paid(self.appointment))

    def test_has_paid_returns_true_after_payment(self):
        """has_paid should return True after a successful payment."""
        txn = AppointmentPaymentService.initiate_payment(
            appointment=self.appointment,
            provider=PaymentProvider.STRIPE,
        )
        AppointmentPaymentService.confirm_payment(txn, provider_payment_id="pi_ok")
        self.assertTrue(AppointmentPaymentService.has_paid(self.appointment))

    def test_subscription_flow_unaffected(self):
        """Subscription records must be unaffected by appointment payment service."""
        from tech_articles.billing.models import Plan, Subscription

        plan = Plan.objects.create(
            name="Pro",
            price=Decimal("9.99"),
            currency=CurrencyChoices.USD,
            interval=PlanInterval.MONTH,
            provider=PaymentProvider.STRIPE,
        )
        sub = Subscription.objects.create(
            user=self.user,
            plan=plan,
            provider=PaymentProvider.STRIPE,
            status=PaymentStatus.PENDING,
        )

        # Initiating appointment payment should not touch subscription records
        AppointmentPaymentService.initiate_payment(
            appointment=self.appointment,
            provider=PaymentProvider.STRIPE,
        )

        sub.refresh_from_db()
        self.assertEqual(sub.status, PaymentStatus.PENDING)


# ============================================================================
# AppointmentPaymentCreateView
# ============================================================================


class AppointmentPaymentCreateViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = _make_user()
        self.client.login(email=self.user.email, password="pass")
        self.appointment = _make_appointment(self.user)
        self.url = reverse("billing:appointment_payment_create")

    def test_requires_login(self):
        """Anonymous users should be redirected."""
        self.client.logout()
        response = self.client.post(
            self.url,
            {"appointment_id": str(self.appointment.id), "gateway": "stripe"},
        )
        self.assertEqual(response.status_code, 302)

    def test_missing_appointment_id_returns_400(self):
        """Missing appointment_id should return 400."""
        response = self.client.post(self.url, {"gateway": "stripe"})
        self.assertEqual(response.status_code, 400)

    def test_invalid_gateway_returns_400(self):
        """Invalid gateway should return 400."""
        response = self.client.post(
            self.url,
            {"appointment_id": str(self.appointment.id), "gateway": "bitcoin"},
        )
        self.assertEqual(response.status_code, 400)

    def test_already_paid_appointment_returns_400(self):
        """Already-paid appointment should return 400."""
        self.appointment.payment_status = PaymentStatus.SUCCEEDED
        self.appointment.save()
        response = self.client.post(
            self.url,
            {"appointment_id": str(self.appointment.id), "gateway": "stripe"},
        )
        self.assertEqual(response.status_code, 400)

    @patch("tech_articles.billing.views.appointment_payment_views.StripeService.create_appointment_checkout_session")
    def test_stripe_create_returns_checkout_url(self, mock_stripe):
        """Successful Stripe create should return checkout_url in JSON."""
        mock_stripe.return_value = "https://checkout.stripe.com/test"
        response = self.client.post(
            self.url,
            {"appointment_id": str(self.appointment.id), "gateway": "stripe"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["gateway"], "stripe")
        self.assertIn("checkout_url", data)
        self.assertIn("transaction_id", data)

    @patch("tech_articles.billing.views.appointment_payment_views.PayPalService.create_appointment_order")
    def test_paypal_create_returns_approval_url(self, mock_paypal):
        """Successful PayPal create should return approval_url in JSON."""
        mock_paypal.return_value = "https://paypal.com/approve"
        response = self.client.post(
            self.url,
            {"appointment_id": str(self.appointment.id), "gateway": "paypal"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["gateway"], "paypal")
        self.assertIn("approval_url", data)


# ============================================================================
# Stripe Webhook — Appointment Payment
# ============================================================================


class StripeWebhookAppointmentTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = _make_user()
        self.appointment = _make_appointment(self.user)
        self.url = reverse("billing:stripe_webhook")

    def _post_event(self, event_dict):
        return self.client.post(
            self.url,
            data=json.dumps(event_dict),
            content_type="application/json",
        )

    def _make_txn(self):
        return AppointmentPaymentService.initiate_payment(
            appointment=self.appointment,
            provider=PaymentProvider.STRIPE,
        )

    def test_checkout_completed_confirms_appointment(self):
        """checkout.session.completed with appointment metadata should confirm appointment."""
        txn = self._make_txn()

        event = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_123",
                    "metadata": {
                        "appointment_id": str(self.appointment.id),
                        "payment_txn_id": str(txn.id),
                    },
                    "amount_total": 5000,
                    "currency": "usd",
                }
            },
        }

        with self.settings(STRIPE_WEBHOOK_SECRET=""):
            response = self._post_event(event)

        self.assertEqual(response.status_code, 200)
        txn.refresh_from_db()
        self.appointment.refresh_from_db()
        self.assertEqual(txn.status, PaymentStatus.SUCCEEDED)
        self.assertTrue(txn.webhook_processed)
        self.assertEqual(self.appointment.status, AppointmentStatus.CONFIRMED)
        self.assertIsNotNone(self.appointment.confirmed_at)

    def test_checkout_completed_idempotent(self):
        """Duplicate webhook events should be ignored (idempotency)."""
        txn = self._make_txn()

        event = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_456",
                    "metadata": {
                        "appointment_id": str(self.appointment.id),
                        "payment_txn_id": str(txn.id),
                    },
                    "amount_total": 5000,
                    "currency": "usd",
                }
            },
        }

        with self.settings(STRIPE_WEBHOOK_SECRET=""):
            self._post_event(event)
            self._post_event(event)  # second time — must be no-op

        txn.refresh_from_db()
        self.assertEqual(txn.status, PaymentStatus.SUCCEEDED)

    def test_checkout_completed_amount_mismatch_does_not_confirm(self):
        """Webhook with wrong amount should NOT confirm the appointment."""
        txn = self._make_txn()

        event = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_789",
                    "metadata": {
                        "appointment_id": str(self.appointment.id),
                        "payment_txn_id": str(txn.id),
                    },
                    "amount_total": 1,  # wrong amount
                    "currency": "usd",
                }
            },
        }

        with self.settings(STRIPE_WEBHOOK_SECRET=""):
            self._post_event(event)

        txn.refresh_from_db()
        self.appointment.refresh_from_db()
        self.assertNotEqual(txn.status, PaymentStatus.SUCCEEDED)
        self.assertNotEqual(self.appointment.status, AppointmentStatus.CONFIRMED)


# ============================================================================
# PayPal Webhook — Appointment Payment
# ============================================================================


class PayPalWebhookAppointmentTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = _make_user()
        self.appointment = _make_appointment(self.user)
        self.url = reverse("billing:paypal_webhook")

    def _post_event(self, event_dict):
        return self.client.post(
            self.url,
            data=json.dumps(event_dict),
            content_type="application/json",
        )

    def _make_txn(self, payment_id="PP_ORDER_001"):
        txn = AppointmentPaymentService.initiate_payment(
            appointment=self.appointment,
            provider=PaymentProvider.PAYPAL,
        )
        txn.provider_payment_id = payment_id
        txn.save(update_fields=["provider_payment_id", "updated_at"])
        return txn

    def test_capture_completed_confirms_appointment(self):
        """PAYMENT.CAPTURE.COMPLETED should confirm the appointment."""
        txn = self._make_txn()

        event = {
            "event_type": "PAYMENT.CAPTURE.COMPLETED",
            "resource": {
                "id": "CAP_001",
                "custom_id": str(self.appointment.id),
                "status": "COMPLETED",
            },
        }

        with self.settings(PAYPAL_WEBHOOK_ID=""):
            response = self._post_event(event)

        self.assertEqual(response.status_code, 200)
        txn.refresh_from_db()
        self.appointment.refresh_from_db()
        self.assertEqual(txn.status, PaymentStatus.SUCCEEDED)
        self.assertEqual(self.appointment.status, AppointmentStatus.CONFIRMED)
        self.assertIsNotNone(self.appointment.confirmed_at)

    def test_capture_denied_marks_transaction_failed(self):
        """PAYMENT.CAPTURE.DENIED should mark transaction as failed."""
        txn = self._make_txn()

        event = {
            "event_type": "PAYMENT.CAPTURE.DENIED",
            "resource": {
                "id": "CAP_002",
                "custom_id": str(self.appointment.id),
            },
        }

        with self.settings(PAYPAL_WEBHOOK_ID=""):
            response = self._post_event(event)

        self.assertEqual(response.status_code, 200)
        txn.refresh_from_db()
        self.appointment.refresh_from_db()
        self.assertEqual(txn.status, PaymentStatus.FAILED)
        self.assertNotEqual(self.appointment.status, AppointmentStatus.CONFIRMED)

    def test_subscription_events_remain_unaffected(self):
        """PayPal subscription webhook events must not affect appointment payment logic."""
        # No appointment transactions exist for this resource — should be 200 with no error
        event = {
            "event_type": "BILLING.SUBSCRIPTION.ACTIVATED",
            "resource": {
                "id": "I-NONEXISTENT123",
                "custom_id": "00000000-0000-0000-0000-000000000000",
            },
        }

        with self.settings(PAYPAL_WEBHOOK_ID=""):
            response = self._post_event(event)

        self.assertEqual(response.status_code, 200)
