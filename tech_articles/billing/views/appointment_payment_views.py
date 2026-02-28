"""
Appointment payment views: create payment intent/order, summary, success, and PayPal return.
Strictly separated from subscription and article-purchase payment logic.
"""
from __future__ import annotations

import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import TemplateView

from tech_articles.appointments.models import Appointment
from tech_articles.billing.models import PaymentTransaction
from tech_articles.billing.services import (
    AppointmentPaymentService,
    StripeService,
    PayPalService,
)
from tech_articles.utils.enums import PaymentProvider, PaymentStatus

logger = logging.getLogger(__name__)


class AppointmentPaymentCreateView(LoginRequiredMixin, View):
    """
    POST /billing/appointments/create/
    Creates a PaymentTransaction and a Stripe PaymentIntent/Checkout session or
    PayPal order for the given appointment.
    Returns JSON with:
      - For Stripe: {"gateway": "stripe", "checkout_url": "..."}
      - For PayPal: {"gateway": "paypal", "approval_url": "..."}
    """

    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        appointment_id = request.POST.get("appointment_id") or request.POST.get("appointment")
        gateway = request.POST.get("gateway", PaymentProvider.STRIPE)

        if not appointment_id:
            return JsonResponse({"error": str(_("Missing appointment ID."))}, status=400)

        appointment = get_object_or_404(
            Appointment, id=appointment_id, user=request.user
        )

        if appointment.payment_status == PaymentStatus.SUCCEEDED:
            return JsonResponse(
                {"error": str(_("This appointment has already been paid."))}, status=400
            )

        valid_gateways = [PaymentProvider.STRIPE, PaymentProvider.PAYPAL]
        if gateway not in valid_gateways:
            return JsonResponse({"error": str(_("Invalid payment gateway."))}, status=400)

        try:
            payment_txn = AppointmentPaymentService.initiate_payment(
                appointment=appointment,
                provider=gateway,
            )

            if gateway == PaymentProvider.STRIPE:
                checkout_url = StripeService.create_appointment_checkout_session(
                    appointment=appointment,
                    payment_txn=payment_txn,
                    request=request,
                )
                return JsonResponse(
                    {
                        "gateway": "stripe",
                        "checkout_url": checkout_url,
                        "transaction_id": str(payment_txn.id),
                    }
                )

            if gateway == PaymentProvider.PAYPAL:
                approval_url = PayPalService.create_appointment_order(
                    appointment=appointment,
                    payment_txn=payment_txn,
                    request=request,
                )
                return JsonResponse(
                    {
                        "gateway": "paypal",
                        "approval_url": approval_url,
                        "transaction_id": str(payment_txn.id),
                    }
                )

        except ValueError as exc:
            return JsonResponse({"error": str(exc)}, status=400)
        except Exception as exc:
            logger.exception("Error initiating appointment payment: %s", exc)
            return JsonResponse(
                {"error": str(_("An error occurred. Please try again."))}, status=500
            )


class AppointmentPaymentSummaryView(LoginRequiredMixin, TemplateView):
    """
    GET /billing/appointments/summary/<transaction_id>/
    Renders the payment summary page for an appointment.
    """

    template_name = "tech-articles/home/pages/billing/appointment_payment_summary.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        payment_txn = get_object_or_404(
            PaymentTransaction,
            id=self.kwargs["transaction_id"],
            appointment__user=self.request.user,
        )
        context["payment_txn"] = payment_txn
        context["appointment"] = payment_txn.appointment
        return context


class AppointmentPaymentSuccessView(LoginRequiredMixin, TemplateView):
    """
    GET /billing/appointments/success/<transaction_id>/
    Success page shown after a confirmed appointment payment.
    Also handles Stripe return (session_id query param) for immediate confirmation.
    """

    template_name = "tech-articles/home/pages/billing/appointment_payment_success.html"

    def get(self, request, *args, **kwargs):
        payment_txn = get_object_or_404(
            PaymentTransaction,
            id=self.kwargs["transaction_id"],
            appointment__user=request.user,
        )

        # Handle Stripe redirect: attempt to confirm from session if still pending
        session_id = request.GET.get("session_id", "")
        if session_id and payment_txn.status == PaymentStatus.PENDING:
            try:
                session = StripeService.retrieve_checkout_session(session_id)
                if not payment_txn.webhook_processed:
                    AppointmentPaymentService.confirm_payment(
                        payment_txn=payment_txn,
                        provider_payment_id=session_id,
                        raw=session if isinstance(session, dict) else dict(session),
                    )
                    payment_txn.webhook_processed = True
                    payment_txn.save(update_fields=["webhook_processed", "updated_at"])
            except Exception as exc:
                logger.warning("Stripe appointment success callback error: %s", exc)

        context = self.get_context_data(**kwargs)
        context["payment_txn"] = payment_txn
        context["appointment"] = payment_txn.appointment
        return self.render_to_response(context)


class AppointmentPaymentPayPalReturnView(LoginRequiredMixin, View):
    """
    GET /billing/appointments/paypal-return/<transaction_id>/
    PayPal return URL after user approves the order.
    Captures the payment and confirms the appointment.
    """

    def get(self, request, *args, **kwargs):
        payment_txn = get_object_or_404(
            PaymentTransaction,
            id=self.kwargs["transaction_id"],
            appointment__user=request.user,
        )
        appointment = payment_txn.appointment

        try:
            if payment_txn.status == PaymentStatus.PENDING and payment_txn.provider_payment_id:
                capture_data = PayPalService.capture_order(payment_txn.provider_payment_id)
                capture_status = capture_data.get("status", "")
                if capture_status == "COMPLETED":
                    if not payment_txn.webhook_processed:
                        AppointmentPaymentService.confirm_payment(
                            payment_txn=payment_txn,
                            provider_payment_id=payment_txn.provider_payment_id,
                            raw=capture_data,
                        )
                        payment_txn.webhook_processed = True
                        payment_txn.save(update_fields=["webhook_processed", "updated_at"])
                    return redirect(
                        "billing:appointment_payment_success",
                        transaction_id=payment_txn.id,
                    )
                else:
                    logger.warning(
                        "PayPal appointment capture status %s for txn %s",
                        capture_status,
                        payment_txn.id,
                    )
                    messages.error(
                        request,
                        _("Payment could not be confirmed. Please contact support."),
                    )
                    return redirect(
                        "billing:appointment_payment_summary",
                        transaction_id=payment_txn.id,
                    )
        except Exception as exc:
            logger.exception("PayPal appointment return error: %s", exc)
            messages.error(request, _("An error occurred. Please try again."))
            return redirect(
                "billing:appointment_payment_summary",
                transaction_id=payment_txn.id,
            )

        return redirect(
            "billing:appointment_payment_success",
            transaction_id=payment_txn.id,
        )
