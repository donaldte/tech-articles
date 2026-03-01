"""
Purchase service: business logic for one-time article purchases.
Separate from subscription logic to keep flows independent.
"""
from __future__ import annotations

import uuid
import logging
from decimal import Decimal

from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from tech_articles.billing.models import Purchase, PaymentTransaction
from tech_articles.content.models import Article
from tech_articles.utils.enums import PaymentProvider, PaymentStatus

logger = logging.getLogger(__name__)


class PurchaseService:
    """Handles article purchase lifecycle: initiate, confirm, cancel."""

    # ------------------------------------------------------------------
    # Read helpers
    # ------------------------------------------------------------------

    @staticmethod
    def has_purchased(user, article: Article) -> bool:
        """Return True if the user has a succeeded purchase for this article."""
        if not user or not user.is_authenticated:
            return False
        return Purchase.objects.filter(
            user=user,
            article=article,
            status=PaymentStatus.SUCCEEDED,
        ).exists()

    @staticmethod
    def get_user_purchases(user):
        """Return all purchases for a user ordered by date."""
        return (
            Purchase.objects.filter(user=user)
            .select_related("article")
            .order_by("-created_at")
        )

    @staticmethod
    def get_user_purchase_transactions(user):
        """Return PaymentTransactions linked to the user's article purchases."""
        purchase_ct = ContentType.objects.get_for_model(Purchase)
        purchase_ids = list(
            Purchase.objects.filter(user=user).values_list("id", flat=True)
        )
        return PaymentTransaction.objects.filter(
            content_type=purchase_ct,
            object_id__in=[str(pid) for pid in purchase_ids],
        ).order_by("-created_at")

    # ------------------------------------------------------------------
    # Write helpers
    # ------------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def initiate_purchase(
        user, article: Article, provider: str
    ) -> tuple[Purchase, PaymentTransaction]:
        """
        Create (or reuse) a pending Purchase and a new PaymentTransaction.

        Idempotency: if a pending purchase already exists for this user/article,
        reuse it but always create a fresh transaction (previous attempt may have failed).

        Returns (purchase, transaction).
        """
        if not article.price or article.price <= 0:
            raise ValueError(_("This article is not available for purchase."))

        # Check if already purchased (succeeded)
        if PurchaseService.has_purchased(user, article):
            raise ValueError(_("You have already purchased this article."))

        # Reuse existing pending purchase or create a new one
        purchase, _ = Purchase.objects.get_or_create(
            user=user,
            article=article,
            defaults={
                "provider": provider,
                "amount": article.price,
                "currency": article.currency,
                "status": PaymentStatus.PENDING,
            },
        )

        # If existing purchase was failed/cancelled, reset it
        if purchase.status in (PaymentStatus.FAILED, PaymentStatus.CANCELLED):
            purchase.provider = provider
            purchase.amount = article.price
            purchase.currency = article.currency
            purchase.status = PaymentStatus.PENDING
            purchase.provider_payment_id = ""
            purchase.save(
                update_fields=[
                    "provider",
                    "amount",
                    "currency",
                    "status",
                    "provider_payment_id",
                    "updated_at",
                ]
            )

        purchase_ct = ContentType.objects.get_for_model(Purchase)
        idempotency_key = f"purchase-{user.id}-{article.id}-{uuid.uuid4().hex[:8]}"

        payment_txn = PaymentTransaction.objects.create(
            provider=provider,
            kind="one_time",
            amount=article.price,
            currency=article.currency,
            status=PaymentStatus.PENDING,
            content_type=purchase_ct,
            object_id=str(purchase.id),
            idempotency_key=idempotency_key,
        )

        logger.info(
            "Initiated purchase %s for user %s, article %s (provider: %s)",
            purchase.id,
            user.id,
            article.id,
            provider,
        )
        return purchase, payment_txn

    @staticmethod
    @transaction.atomic
    def confirm_purchase(
        purchase: Purchase,
        payment_txn: PaymentTransaction,
        provider_payment_id: str = "",
        raw: dict | None = None,
    ) -> None:
        """
        Mark the purchase and its transaction as succeeded.
        Grants the user immediate access to the article.
        Invalidates the billing cache.
        """
        purchase.status = PaymentStatus.SUCCEEDED
        if provider_payment_id:
            purchase.provider_payment_id = provider_payment_id
        purchase.save(update_fields=["status", "provider_payment_id", "updated_at"])

        payment_txn.mark_succeeded(provider_payment_id=provider_payment_id, raw=raw)

        # Invalidate cache so access check is refreshed
        from tech_articles.billing.cache import BillingCache

        try:
            from django.contrib.auth import get_user_model

            User = get_user_model()
            user = User.objects.get(id=purchase.user_id)
            BillingCache.clear_purchased_articles_cache(user)
        except Exception as exc:
            logger.warning("Could not clear purchase cache for user %s: %s", purchase.user_id, exc)

        logger.info(
            "Confirmed purchase %s for article %s (provider_payment_id: %s)",
            purchase.id,
            purchase.article_id,
            provider_payment_id,
        )

        # Track analytics event
        from tech_articles.analytics.services import create_event
        from tech_articles.utils.enums import EventType
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.get(id=purchase.user_id)
            create_event(
                event_type=EventType.ARTICLE_PURCHASE,
                user=user,
                metadata={
                    "purchase_id": str(purchase.id),
                    "article_id": str(purchase.article_id),
                    "article_title": purchase.article.title if purchase.article else "",
                    "amount": str(purchase.amount),
                    "currency": purchase.currency,
                    "provider": purchase.provider,
                },
            )
        except Exception:
            logger.exception("Failed to create ARTICLE_PURCHASE event")

    @staticmethod
    @transaction.atomic
    def cancel_purchase(purchase: Purchase, payment_txn: PaymentTransaction | None = None) -> None:
        """Mark a pending purchase and its transaction as cancelled."""
        if purchase.status == PaymentStatus.PENDING:
            purchase.status = PaymentStatus.CANCELLED
            purchase.save(update_fields=["status", "updated_at"])

        if payment_txn and payment_txn.status == PaymentStatus.PENDING:
            payment_txn.status = PaymentStatus.CANCELLED
            payment_txn.save(update_fields=["status", "updated_at"])

        logger.info("Cancelled purchase %s", purchase.id)
