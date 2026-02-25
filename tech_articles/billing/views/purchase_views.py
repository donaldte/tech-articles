"""
Article purchase views: checkout, success, cancel, PayPal return.
Kept entirely separate from subscription views.
"""
import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView, View

from tech_articles.billing.models import Purchase, PaymentTransaction
from tech_articles.billing.services import PurchaseService, StripeService, PayPalService
from tech_articles.content.models import Article
from tech_articles.utils.enums import ArticleAccessType, PaymentProvider, PaymentStatus

logger = logging.getLogger(__name__)


class ArticlePurchaseCheckoutView(LoginRequiredMixin, TemplateView):
    """
    Purchase checkout page: shows article summary, price and payment method selector.
    On POST, initiates the payment session via the chosen provider.
    """

    template_name = "tech-articles/home/pages/billing/purchase_checkout.html"

    def _get_article(self):
        return get_object_or_404(
            Article,
            slug=self.kwargs["slug"],
            access_type=ArticleAccessType.PAID,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self._get_article()
        context["article"] = article
        context["already_purchased"] = PurchaseService.has_purchased(self.request.user, article)
        return context

    def post(self, request, *args, **kwargs):
        article = self._get_article()
        provider = request.POST.get("provider", PaymentProvider.STRIPE)

        # Server-side validation: article must be paid and have a price
        if article.access_type != ArticleAccessType.PAID or not article.price or article.price <= 0:
            messages.error(request, _("This article is not available for purchase."))
            return redirect(request.path)

        # Already purchased?
        if PurchaseService.has_purchased(request.user, article):
            messages.info(request, _("You have already purchased this article."))
            return redirect(article.get_absolute_url())

        valid_providers = [PaymentProvider.STRIPE, PaymentProvider.PAYPAL]
        if provider not in valid_providers:
            messages.error(request, _("Invalid payment provider."))
            return redirect(request.path)

        try:
            purchase, payment_txn = PurchaseService.initiate_purchase(
                user=request.user,
                article=article,
                provider=provider,
            )

            if provider == PaymentProvider.STRIPE:
                checkout_url = StripeService.create_purchase_checkout_session(
                    purchase=purchase,
                    payment_txn=payment_txn,
                    request=request,
                )
                return redirect(checkout_url)

            if provider == PaymentProvider.PAYPAL:
                approval_url = PayPalService.create_purchase_order(
                    purchase=purchase,
                    payment_txn=payment_txn,
                    request=request,
                )
                return redirect(approval_url)

        except ValueError as exc:
            messages.error(request, str(exc))
            return redirect(request.path)
        except Exception as exc:
            logger.exception("Error initiating article purchase: %s", exc)
            messages.error(request, _("An error occurred. Please try again."))
            return redirect(request.path)


class PurchaseStripeSuccessView(LoginRequiredMixin, View):
    """
    Stripe Checkout success return URL for article purchases.
    The actual confirmation is handled by the webhook; this page confirms immediately
    from the session data so the user gets instant access.
    """

    def get(self, request, *args, **kwargs):
        session_id = request.GET.get("session_id", "")
        if session_id:
            try:
                session = StripeService.retrieve_checkout_session(session_id)
                metadata = session.get("metadata", {})
                purchase_id = metadata.get("purchase_id")
                txn_id = metadata.get("payment_txn_id")

                if purchase_id and txn_id:
                    purchase = Purchase.objects.filter(
                        id=purchase_id, user=request.user
                    ).first()
                    payment_txn = PaymentTransaction.objects.filter(id=txn_id).first()
                    if purchase and payment_txn and purchase.status == PaymentStatus.PENDING:
                        PurchaseService.confirm_purchase(
                            purchase=purchase,
                            payment_txn=payment_txn,
                            provider_payment_id=session_id,
                            raw=session if isinstance(session, dict) else dict(session),
                        )
                        payment_txn.webhook_processed = True
                        payment_txn.save(update_fields=["webhook_processed", "updated_at"])
            except Exception as exc:
                logger.warning("Stripe purchase success callback error: %s", exc)

        messages.success(
            request,
            _("Payment successful! You now have full access to this article."),
        )
        return redirect("dashboard:my_articles")


class PurchasePayPalReturnView(LoginRequiredMixin, View):
    """
    PayPal return URL after the user approves the order on PayPal.
    Captures the payment and confirms the purchase.
    """

    def get(self, request, *args, **kwargs):
        purchase_id = request.GET.get("purchase_id", "")
        txn_id = request.GET.get("txn_id", "")

        try:
            purchase = Purchase.objects.get(id=purchase_id, user=request.user)
            payment_txn = PaymentTransaction.objects.get(id=txn_id)

            if purchase.status == PaymentStatus.PENDING and payment_txn.provider_payment_id:
                capture_data = PayPalService.capture_order(payment_txn.provider_payment_id)
                capture_status = capture_data.get("status", "")
                if capture_status == "COMPLETED":
                    PurchaseService.confirm_purchase(
                        purchase=purchase,
                        payment_txn=payment_txn,
                        provider_payment_id=payment_txn.provider_payment_id,
                        raw=capture_data,
                    )
                    payment_txn.webhook_processed = True
                    payment_txn.save(update_fields=["webhook_processed", "updated_at"])
                else:
                    logger.warning(
                        "PayPal order capture status %s for purchase %s",
                        capture_status,
                        purchase_id,
                    )
                    messages.error(
                        request,
                        _("Payment could not be confirmed. Please contact support."),
                    )
                    return redirect("dashboard:my_purchases")

            messages.success(
                request,
                _("Payment successful! You now have full access to this article."),
            )
        except (Purchase.DoesNotExist, PaymentTransaction.DoesNotExist) as exc:
            logger.error("PayPal purchase return: object not found: %s", exc)
            messages.error(request, _("Could not confirm your payment. Please contact support."))
        except Exception as exc:
            logger.exception("PayPal purchase return error: %s", exc)
            messages.error(request, _("An error occurred. Please try again."))

        return redirect("dashboard:my_articles")


class PurchaseCancelView(LoginRequiredMixin, View):
    """
    Cancel page: shown when the user abandons the checkout.
    Marks the pending purchase as cancelled.
    """

    template_name = "tech-articles/home/pages/billing/purchase_cancel.html"

    def get(self, request, *args, **kwargs):
        purchase = get_object_or_404(Purchase, id=kwargs["pk"], user=request.user)

        # Cancel the pending transaction if it exists
        purchase_ct = ContentType.objects.get_for_model(Purchase)
        payment_txn = PaymentTransaction.objects.filter(
            content_type=purchase_ct,
            object_id=str(purchase.id),
            status=PaymentStatus.PENDING,
        ).first()

        PurchaseService.cancel_purchase(purchase=purchase, payment_txn=payment_txn)

        from django.shortcuts import render

        return render(
            request,
            self.template_name,
            {"purchase": purchase, "article": purchase.article},
        )
