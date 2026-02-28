"""
Tests for billing admin views (transactions, subscriptions).
"""
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from tech_articles.billing.models import PaymentTransaction, Plan, Subscription
from tech_articles.utils.enums import PaymentProvider, PaymentStatus, PlanInterval, CurrencyChoices

User = get_user_model()


class _AdminSetupMixin:
    """Mixin that creates a staff/admin user and logs in."""

    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            email="admin@example.com",
            password="adminpass123",
            is_staff=True,
        )
        self.client.login(email="admin@example.com", password="adminpass123")

        self.regular_user = User.objects.create_user(
            email="user@example.com",
            password="userpass123",
        )


class TransactionListViewTestCase(_AdminSetupMixin, TestCase):
    """Tests for TransactionListView admin page."""

    def _make_txn(self, **kwargs):
        defaults = {
            "provider": PaymentProvider.STRIPE,
            "kind": "one_time",
            "status": PaymentStatus.SUCCEEDED,
            "amount": "9.99",
            "currency": CurrencyChoices.USD,
        }
        defaults.update(kwargs)
        return PaymentTransaction.objects.create(**defaults)

    def test_admin_can_access_transaction_list(self):
        """Staff user can access the transactions list."""
        self._make_txn()
        url = reverse("billing:transactions_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Payment Transactions")

    def test_anonymous_user_redirected(self):
        """Anonymous users are redirected to login."""
        self.client.logout()
        url = reverse("billing:transactions_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_regular_user_forbidden(self):
        """Non-staff users cannot access the transaction list."""
        self.client.logout()
        self.client.login(email="user@example.com", password="userpass123")
        url = reverse("billing:transactions_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_filter_by_status(self):
        """Filtering by status returns only matching transactions."""
        self._make_txn(status=PaymentStatus.SUCCEEDED)
        self._make_txn(status=PaymentStatus.FAILED)
        url = reverse("billing:transactions_list") + "?status=succeeded"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        txns = response.context["transactions"]
        self.assertTrue(all(t.status == PaymentStatus.SUCCEEDED for t in txns))

    def test_filter_by_gateway(self):
        """Filtering by gateway returns only matching transactions."""
        self._make_txn(provider=PaymentProvider.STRIPE)
        self._make_txn(provider=PaymentProvider.PAYPAL)
        url = reverse("billing:transactions_list") + "?gateway=stripe"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        txns = response.context["transactions"]
        self.assertTrue(all(t.provider == PaymentProvider.STRIPE for t in txns))

    def test_search_by_payment_id(self):
        """Searching by provider_payment_id returns matching transactions."""
        txn = self._make_txn(provider_payment_id="pi_test_12345")
        self._make_txn(provider_payment_id="pi_other_99999")
        url = reverse("billing:transactions_list") + "?search=pi_test_12345"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        txns = list(response.context["transactions"])
        self.assertEqual(len(txns), 1)
        self.assertEqual(txns[0].provider_payment_id, "pi_test_12345")

    def test_pagination(self):
        """Transactions are paginated (page size 25)."""
        for i in range(30):
            self._make_txn(provider_payment_id=f"pi_{i:04d}")
        url = reverse("billing:transactions_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["transactions"]), 25)


class SubscriptionListViewTestCase(_AdminSetupMixin, TestCase):
    """Tests for SubscriptionListView admin page."""

    def _make_plan(self):
        return Plan.objects.create(
            name="Pro",
            price="9.99",
            currency=CurrencyChoices.USD,
            interval=PlanInterval.MONTH,
            provider=PaymentProvider.STRIPE,
        )

    def _make_subscription(self, status=PaymentStatus.SUCCEEDED):
        plan = self._make_plan()
        return Subscription.objects.create(
            user=self.regular_user,
            plan=plan,
            provider=PaymentProvider.STRIPE,
            status=status,
        )

    def test_admin_can_access_subscription_list(self):
        """Staff user can access the subscriptions list."""
        self._make_subscription()
        url = reverse("billing:subscriptions_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "User Subscriptions")

    def test_filter_by_status(self):
        """Filtering by status returns only matching subscriptions."""
        self._make_subscription(status=PaymentStatus.SUCCEEDED)
        self._make_subscription(status=PaymentStatus.CANCELLED)
        url = reverse("billing:subscriptions_list") + "?status=succeeded"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        subs = response.context["subscriptions"]
        self.assertTrue(all(s.status == PaymentStatus.SUCCEEDED for s in subs))

    def test_detail_view_accessible(self):
        """Admin can access subscription detail page."""
        sub = self._make_subscription()
        url = reverse("billing:subscriptions_detail", kwargs={"pk": sub.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["subscription"], sub)
