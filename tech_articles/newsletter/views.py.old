"""
Newsletter views for subscription management.
"""
import csv
import io
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import FormView, TemplateView

from tech_articles.newsletter.forms import (
    NewsletterSubscribeForm,
    NewsletterUnsubscribeForm,
    SubscriberFilterForm,
    SubscriberImportForm,
    SubscriberTagForm,
    SubscriberSegmentForm,
    SubscriberEditForm,
)
from tech_articles.newsletter.models import (
    NewsletterSubscriber,
    SubscriberTag,
    SubscriberSegment,
    SubscriberEngagement,
    EmailLog,
)
from tech_articles.utils.enums import LanguageChoices, SubscriberStatus


# ============================================================================
# PUBLIC VIEWS (User-facing)
# ============================================================================

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


# ============================================================================
# ADMIN DASHBOARD VIEWS (Staff only)
# ============================================================================

class SubscriberListView(LoginRequiredMixin, View):
    """List all newsletter subscribers with filters."""
    
    def get(self, request):
        if not request.user.is_staff:
            messages.error(request, _("You don't have permission to access this page."))
            return redirect("dashboard:index")
        
        # Get filter form
        filter_form = SubscriberFilterForm(request.GET)
        
        # Base queryset
        subscribers = NewsletterSubscriber.objects.all()
        
        # Apply filters
        if filter_form.is_valid():
            status = filter_form.cleaned_data.get("status")
            language = filter_form.cleaned_data.get("language")
            is_confirmed = filter_form.cleaned_data.get("is_confirmed")
            search = filter_form.cleaned_data.get("search")
            
            if status:
                subscribers = subscribers.filter(status=status)
            if language:
                subscribers = subscribers.filter(language=language)
            if is_confirmed == "yes":
                subscribers = subscribers.filter(is_confirmed=True)
            elif is_confirmed == "no":
                subscribers = subscribers.filter(is_confirmed=False)
            if search:
                subscribers = subscribers.filter(
                    Q(email__icontains=search)
                )
        
        # Annotate with engagement count
        subscribers = subscribers.annotate(
            engagement_count=Count("engagements")
        )
        
        # Pagination
        paginator = Paginator(subscribers, 25)
        page_number = request.GET.get("page", 1)
        page_obj = paginator.get_page(page_number)
        
        # Statistics
        stats = {
            "total": NewsletterSubscriber.objects.count(),
            "active": NewsletterSubscriber.objects.filter(status=SubscriberStatus.ACTIVE).count(),
            "confirmed": NewsletterSubscriber.objects.filter(is_confirmed=True).count(),
            "bounced": NewsletterSubscriber.objects.filter(status=SubscriberStatus.BOUNCED).count(),
        }
        
        return render(request, "tech-articles/dashboard/pages/newsletter/subscribers/list.html", {
            "page_obj": page_obj,
            "filter_form": filter_form,
            "stats": stats,
        })


class SubscriberExportView(LoginRequiredMixin, View):
    """Export subscribers to CSV."""
    
    def get(self, request):
        if not request.user.is_staff:
            messages.error(request, _("You don't have permission to access this page."))
            return redirect("dashboard:index")
        
        # Create CSV response
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="subscribers.csv"'
        
        writer = csv.writer(response)
        writer.writerow(["Email", "Language", "Status", "Confirmed", "Created At"])
        
        # Write subscriber data
        subscribers = NewsletterSubscriber.objects.all()
        for subscriber in subscribers:
            writer.writerow([
                subscriber.email,
                subscriber.language,
                subscriber.status,
                "Yes" if subscriber.is_confirmed else "No",
                subscriber.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            ])
        
        return response


class SubscriberImportView(LoginRequiredMixin, FormView):
    """Import subscribers from CSV."""
    template_name = "tech-articles/dashboard/pages/newsletter/subscribers/import.html"
    form_class = SubscriberImportForm
    success_url = reverse_lazy("newsletter:admin_list")
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, _("You don't have permission to access this page."))
            return redirect("dashboard:index")
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        csv_file = form.cleaned_data["csv_file"]
        content = csv_file.read().decode("utf-8")
        reader = csv.DictReader(io.StringIO(content))
        
        created_count = 0
        skipped_count = 0
        
        for row in reader:
            email = row.get("email", "").strip().lower()
            language = row.get("language", LanguageChoices.FR).strip().lower()
            
            if not email:
                continue
            
            # Validate language
            if language not in dict(LanguageChoices.choices):
                language = LanguageChoices.FR
            
            # Create subscriber if not exists
            if not NewsletterSubscriber.objects.filter(email__iexact=email).exists():
                NewsletterSubscriber.objects.create(
                    email=email,
                    language=language,
                    is_confirmed=True,
                    is_active=True,
                    status=SubscriberStatus.ACTIVE,
                    consent_given_at=timezone.now(),
                )
                created_count += 1
            else:
                skipped_count += 1
        
        messages.success(
            self.request,
            _("Import completed: %(created)d created, %(skipped)d skipped") % {
                "created": created_count,
                "skipped": skipped_count,
            },
        )
        
        return super().form_valid(form)


class SubscriberDetailView(LoginRequiredMixin, View):
    """View subscriber details and engagement history."""
    
    def get(self, request, subscriber_id):
        if not request.user.is_staff:
            messages.error(request, _("You don't have permission to access this page."))
            return redirect("dashboard:index")
        
        subscriber = get_object_or_404(NewsletterSubscriber, id=subscriber_id)
        
        # Get engagement history
        engagements = SubscriberEngagement.objects.filter(
            subscriber=subscriber
        ).select_related("email_log")[:50]
        
        # Get email logs
        email_logs = EmailLog.objects.filter(
            to_email=subscriber.email
        )[:20]
        
        return render(request, "tech-articles/dashboard/pages/newsletter/subscribers/detail.html", {
            "subscriber": subscriber,
            "engagements": engagements,
            "email_logs": email_logs,
        })


class SubscriberEditView(LoginRequiredMixin, FormView):
    """Edit subscriber details."""
    template_name = "tech-articles/dashboard/pages/newsletter/subscribers/edit.html"
    form_class = SubscriberEditForm
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, _("You don't have permission to access this page."))
            return redirect("dashboard:index")
        
        self.subscriber = get_object_or_404(
            NewsletterSubscriber,
            id=kwargs.get("subscriber_id"),
        )
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.subscriber
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["subscriber"] = self.subscriber
        return context
    
    def form_valid(self, form):
        form.save()
        messages.success(self.request, _("Subscriber updated successfully."))
        return redirect("newsletter:admin_detail", subscriber_id=self.subscriber.id)
    
    def get_success_url(self):
        return reverse("newsletter:admin_detail", kwargs={"subscriber_id": self.subscriber.id})

