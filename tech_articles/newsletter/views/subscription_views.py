"""
Newsletter public subscription views.
"""
import logging

from django.http import JsonResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect

from tech_articles.newsletter.models import NewsletterSubscriber
from tech_articles.newsletter.forms import NewsletterSubscriptionForm
from tech_articles.utils.enums import SubscriberStatus

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Extract client IP address from request."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


@csrf_protect
@require_http_methods(["POST"])
def subscribe_newsletter(request):
    """
    Public endpoint for newsletter subscription.
    Returns JSON response with success/error message.
    """
    form = NewsletterSubscriptionForm(request.POST)
    
    if form.is_valid():
        try:
            subscriber = form.save(commit=False)
            subscriber.is_active = True
            subscriber.is_confirmed = False  # Require email confirmation
            subscriber.status = SubscriberStatus.ACTIVE
            subscriber.consent_given_at = timezone.now()
            subscriber.ip_address = get_client_ip(request)
            subscriber.save()
            
            logger.info(f"New newsletter subscription: {subscriber.email}")
            
            return JsonResponse({
                "success": True,
                "message": str(_("Thank you for subscribing to our newsletter!")),
            })
        except Exception as e:
            logger.error(f"Error during subscription: {str(e)}")
            return JsonResponse({
                "success": False,
                "message": str(_("An error occurred. Please try again later.")),
            }, status=500)
    else:
        errors = {}
        for field, error_list in form.errors.items():
            errors[field] = [str(error) for error in error_list]
        
        return JsonResponse({
            "success": False,
            "message": str(_("Please correct the errors below.")),
            "errors": errors,
        }, status=400)


@require_http_methods(["POST"])
def unsubscribe_newsletter(request, token):
    """
    One-click unsubscribe endpoint (POST only).
    Returns JSON response with success/error message.
    """
    try:
        subscriber = NewsletterSubscriber.objects.get(unsub_token=token)
    except NewsletterSubscriber.DoesNotExist:
        return JsonResponse({
            "success": False,
            "message": str(_("Invalid unsubscribe link.")),
        }, status=404)
    
    subscriber.unsubscribe()
    logger.info(f"Unsubscribed: {subscriber.email}")
    
    return JsonResponse({
        "success": True,
        "message": str(_("You have been successfully unsubscribed.")),
    })
