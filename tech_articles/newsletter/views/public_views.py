"""
Public newsletter views for user-facing subscription management.
"""
from django.contrib import messages
from django.http import Http404
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import FormView, TemplateView

from tech_articles.newsletter.forms import (
    NewsletterSubscribeForm,
    NewsletterUnsubscribeForm,
)
from tech_articles.newsletter.models import NewsletterSubscriber
from tech_articles.utils.enums import SubscriberStatus


class NewsletterSubscribeView(FormView):
    """Handle newsletter subscription with double opt-in."""
    template_name = "tech-articles/newsletter/subscribe.html"
    form_class = NewsletterSubscribeForm
    success_url = reverse_lazy("newsletter:subscribe_pending")

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        language = form.cleaned_data["language"]
        
        # Create subscriber with unconfirmed status
        subscriber = NewsletterSubscriber.objects.create(
            email=email,
            language=language,
            is_confirmed=False,
            is_active=False,
            status=SubscriberStatus.INACTIVE,
            consent_given_at=timezone.now(),
            ip_address=self.get_client_ip(),
        )
        
        # TODO: Send confirmation email with confirm_token
        # send_confirmation_email(subscriber)
        
        messages.success(
            self.request,
            _("Please check your email to confirm your subscription."),
        )
        
        return super().form_valid(form)
    
    def get_client_ip(self):
        """Get client IP address from request."""
        x_forwarded_for = self.request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = self.request.META.get("REMOTE_ADDR")
        return ip


class NewsletterSubscribePendingView(TemplateView):
    """Show pending confirmation message."""
    template_name = "tech-articles/newsletter/subscribe_pending.html"


class NewsletterConfirmView(View):
    """Confirm newsletter subscription via token."""
    
    def get(self, request, token):
        try:
            subscriber = NewsletterSubscriber.objects.get(confirm_token=token)
            
            if subscriber.is_confirmed:
                messages.info(request, _("Your email is already confirmed."))
            else:
                subscriber.confirm()
                messages.success(
                    request,
                    _("Thank you! Your subscription has been confirmed."),
                )
            
            return render(request, "tech-articles/newsletter/confirmed.html", {
                "subscriber": subscriber,
            })
            
        except NewsletterSubscriber.DoesNotExist:
            messages.error(request, _("Invalid confirmation link."))
            return redirect("newsletter:subscribe")


class NewsletterUnsubscribeView(FormView):
    """Handle newsletter unsubscription via token."""
    template_name = "tech-articles/newsletter/unsubscribe.html"
    form_class = NewsletterUnsubscribeForm
    
    def dispatch(self, request, *args, **kwargs):
        token = kwargs.get("token")
        try:
            self.subscriber = NewsletterSubscriber.objects.get(unsub_token=token)
        except NewsletterSubscriber.DoesNotExist:
            raise Http404(_("Invalid unsubscribe link"))
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["subscriber"] = self.subscriber
        return context
    
    def form_valid(self, form):
        self.subscriber.unsubscribe()
        messages.success(
            self.request,
            _("You have been successfully unsubscribed from our newsletter."),
        )
        return redirect("newsletter:unsubscribe_success")


class NewsletterUnsubscribeSuccessView(TemplateView):
    """Show unsubscribe success message."""
    template_name = "tech-articles/newsletter/unsubscribe_success.html"
