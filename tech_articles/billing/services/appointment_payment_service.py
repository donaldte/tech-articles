"""
Appointment payment service: business logic for paid appointment flows.
Strictly separated from subscription and article-purchase payment logic.
"""
from __future__ import annotations

import uuid
import logging
from decimal import Decimal

from django.db import transaction
from django.utils.translation import gettext_lazy as _

from tech_articles.billing.models import PaymentTransaction
from tech_articles.utils.enums import PaymentProvider, PaymentStatus

logger = logging.getLogger(__name__)


class AppointmentPaymentService:
    """Handles appointment payment lifecycle: initiate, confirm, fail."""

    # ------------------------------------------------------------------
    # Read helpers
    # ------------------------------------------------------------------

    @staticmethod
    def has_paid(appointment) -> bool:
        """Return True if the appointment has a completed payment transaction."""
        return PaymentTransaction.objects.filter(
            appointment=appointment,
            status=PaymentStatus.SUCCEEDED,
        ).exists()

    # ------------------------------------------------------------------
    # Write helpers
    # ------------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def initiate_payment(
        appointment,
        provider: str,
    ) -> PaymentTransaction:
        """
        Create a new pending PaymentTransaction for the appointment.

        A new transaction is always created (idempotency is handled via
        idempotency_key; previous failed attempts do not block new ones).

        Returns the new PaymentTransaction.
        """
        from tech_articles.utils.enums import AppointmentStatus

        if appointment.payment_status == PaymentStatus.SUCCEEDED:
            raise ValueError(_("This appointment has already been paid."))

        if not appointment.total_amount or appointment.total_amount <= 0:
            raise ValueError(_("This appointment does not have a valid amount."))

        idempotency_key = f"appt-{appointment.id}-{uuid.uuid4().hex[:12]}"

        payment_txn = PaymentTransaction.objects.create(
            appointment=appointment,
            provider=provider,
            kind="appointment",
            amount=appointment.total_amount,
            currency=appointment.currency,
            status=PaymentStatus.PENDING,
            idempotency_key=idempotency_key,
        )

        # Update appointment's provider field so we know which gateway was used
        appointment.provider = provider
        appointment.payment_status = PaymentStatus.PENDING
        appointment.save(update_fields=["provider", "payment_status", "updated_at"])

        logger.info(
            "Initiated appointment payment %s for appointment %s (provider: %s, amount: %s %s)",
            payment_txn.id,
            appointment.id,
            provider,
            appointment.total_amount,
            appointment.currency,
        )
        return payment_txn

    @staticmethod
    @transaction.atomic
    def confirm_payment(
        payment_txn: PaymentTransaction,
        provider_payment_id: str = "",
        raw: dict | None = None,
    ) -> None:
        """
        Mark the transaction as succeeded, set appointment payment_status to
        succeeded, and call appointment.confirm() to set confirmed status/timestamp.

        Idempotent: if the transaction is already succeeded, this is a no-op.
        """
        if payment_txn.status == PaymentStatus.SUCCEEDED:
            logger.info(
                "Appointment payment %s already confirmed — skipping.", payment_txn.id
            )
            return

        payment_txn.mark_succeeded(provider_payment_id=provider_payment_id, raw=raw)

        appointment = payment_txn.appointment
        if appointment is None:
            logger.error(
                "PaymentTransaction %s has no linked appointment — cannot confirm.",
                payment_txn.id,
            )
            return

        appointment.payment_status = PaymentStatus.SUCCEEDED
        if provider_payment_id:
            appointment.provider_payment_id = provider_payment_id
        appointment.save(
            update_fields=["payment_status", "provider_payment_id", "updated_at"]
        )

        # Confirm the appointment (sets status=CONFIRMED and confirmed_at)
        appointment.confirm()

        logger.info(
            "Confirmed appointment payment %s and appointment %s (provider_payment_id: %s)",
            payment_txn.id,
            appointment.id,
            provider_payment_id,
        )

    @staticmethod
    @transaction.atomic
    def fail_payment(
        payment_txn: PaymentTransaction,
        error_message: str = "",
        raw: dict | None = None,
    ) -> None:
        """
        Mark the transaction as failed and leave the appointment unconfirmed.
        """
        payment_txn.mark_failed(error_message=error_message, raw=raw)
        logger.info(
            "Marked appointment payment %s as failed: %s",
            payment_txn.id,
            error_message,
        )

    @staticmethod
    def amount_matches(payment_txn: PaymentTransaction, amount_cents: int, currency: str) -> bool:
        """
        Validate that the webhook amount matches the recorded transaction amount.
        amount_cents: amount in smallest currency unit (e.g. cents for USD).
        """
        if payment_txn.amount is None:
            return False
        expected_cents = int(payment_txn.amount * 100)
        return (
            expected_cents == amount_cents
            and payment_txn.currency.upper() == currency.upper()
        )
