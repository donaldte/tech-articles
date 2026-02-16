"""
Newsletter subscriber views for dashboard CRUD operations.
"""
import csv
import logging
from io import StringIO

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from tech_articles.newsletter.models import NewsletterSubscriber
from tech_articles.newsletter.forms import NewsletterSubscriberForm
from tech_articles.utils.mixins import AdminRequiredMixin

logger = logging.getLogger(__name__)



class SubscriberListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """List all newsletter subscribers."""
    model = NewsletterSubscriber
    template_name = "tech-articles/dashboard/pages/newsletter/subscribers/list.html"
    context_object_name = "subscribers"
    paginate_by = 10
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get("search", "").strip()
        status = self.request.GET.get("status", "")
        confirmed = self.request.GET.get("confirmed", "")
        language = self.request.GET.get("language", "")
        tag = self.request.GET.get("tag", "").strip()

        if search:
            queryset = queryset.filter(
                Q(email__icontains=search) | Q(tags__icontains=search)
            )

        if status:
            if status == "active":
                queryset = queryset.filter(is_active=True)
            elif status == "inactive":
                queryset = queryset.filter(is_active=False)

        if confirmed == "yes":
            queryset = queryset.filter(is_confirmed=True)
        elif confirmed == "no":
            queryset = queryset.filter(is_confirmed=False)

        if language:
            queryset = queryset.filter(language=language)

        if tag:
            queryset = queryset.filter(tags__icontains=tag)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "")
        context["status"] = self.request.GET.get("status", "")
        context["confirmed"] = self.request.GET.get("confirmed", "")
        context["language"] = self.request.GET.get("language", "")
        context["tag"] = self.request.GET.get("tag", "")

        # Add statistics
        total = NewsletterSubscriber.objects.count()
        active = NewsletterSubscriber.objects.filter(is_active=True).count()
        confirmed = NewsletterSubscriber.objects.filter(is_confirmed=True).count()
        inactive = NewsletterSubscriber.objects.filter(is_active=False).count()

        context["total_count"] = total
        context["active_count"] = active
        context["confirmed_count"] = confirmed
        context["inactive_count"] = inactive

        return context


class SubscriberCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    """Create a new newsletter subscriber."""
    model = NewsletterSubscriber
    form_class = NewsletterSubscriberForm
    template_name = "tech-articles/dashboard/pages/newsletter/subscribers/create.html"
    success_url = reverse_lazy("newsletter:subscribers_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Create Subscriber")
        context["is_edit"] = False
        return context

    def form_valid(self, form):
        messages.success(self.request, _("Subscriber created successfully."))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Please correct the errors below."))
        return super().form_invalid(form)


class SubscriberUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    """Update an existing newsletter subscriber."""
    model = NewsletterSubscriber
    form_class = NewsletterSubscriberForm
    template_name = "tech-articles/dashboard/pages/newsletter/subscribers/edit.html"
    success_url = reverse_lazy("newsletter:subscribers_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Edit Subscriber")
        context["is_edit"] = True
        return context

    def form_valid(self, form):
        messages.success(self.request, _("Subscriber updated successfully."))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Please correct the errors below."))
        return super().form_invalid(form)


class SubscriberDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    """Delete a newsletter subscriber."""
    model = NewsletterSubscriber
    template_name = "tech-articles/dashboard/pages/newsletter/subscribers/delete.html"
    success_url = reverse_lazy("newsletter:subscribers_list")

    def form_valid(self, form):
        messages.success(self.request, _("Subscriber deleted successfully."))
        return super().form_valid(form)


class SubscriberExportCSVView(LoginRequiredMixin, AdminRequiredMixin, View):
    """Export subscribers to CSV."""

    def get(self, request, *args, **kwargs):
        # Create the HttpResponse object with CSV header
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="newsletter_subscribers_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'

        writer = csv.writer(response)
        writer.writerow([
            "Email",
            "Language",
            "Status",
            "Is Active",
            "Is Confirmed",
            "Tags",
            "Email Open Count",
            "Email Click Count",
            "Consent Given At",
            "Created At",
        ])

        # Get filtered queryset based on query params
        queryset = NewsletterSubscriber.objects.all().order_by("-created_at")

        # Apply same filters as list view
        search = request.GET.get("search", "").strip()
        status = request.GET.get("status", "")
        confirmed = request.GET.get("confirmed", "")
        language = request.GET.get("language", "")

        if search:
            queryset = queryset.filter(Q(email__icontains=search) | Q(tags__icontains=search))
        if status:
            if status == "active":
                queryset = queryset.filter(is_active=True)
            elif status == "inactive":
                queryset = queryset.filter(is_active=False)
        if confirmed == "yes":
            queryset = queryset.filter(is_confirmed=True)
        elif confirmed == "no":
            queryset = queryset.filter(is_confirmed=False)
        if language:
            queryset = queryset.filter(language=language)

        for subscriber in queryset:
            writer.writerow([
                subscriber.email,
                subscriber.get_language_display(),
                "Active" if subscriber.is_active else "Inactive",
                subscriber.is_active,
                subscriber.is_confirmed,
                subscriber.tags,
                subscriber.email_open_count,
                subscriber.email_click_count,
                subscriber.consent_given_at.isoformat() if subscriber.consent_given_at else "",
                subscriber.created_at.isoformat(),
            ])

        logger.info(f"Exported {queryset.count()} subscribers to CSV by user {request.user.email}")
        return response


class SubscriberImportCSVView(LoginRequiredMixin, AdminRequiredMixin, View):
    """Import subscribers from CSV."""

    def post(self, request, *args, **kwargs):
        csv_file = request.FILES.get("csv_file")

        if not csv_file:
            return JsonResponse({
                "success": False,
                "message": str(_("No file provided.")),
            }, status=400)

        if not csv_file.name.endswith(".csv"):
            return JsonResponse({
                "success": False,
                "message": str(_("File must be a CSV.")),
            }, status=400)

        try:
            # Read the CSV file
            file_data = csv_file.read().decode("utf-8")
            csv_reader = csv.DictReader(StringIO(file_data))

            created_count = 0
            skipped_count = 0
            errors = []

            for row_num, row in enumerate(csv_reader, start=2):
                # Make keys case-insensitive
                row = {k.lower(): v for k, v in row.items()}

                email = row.get("email", "").strip().lower()
                language = row.get("language", "fr").lower()[:2]
                tags = row.get("tags", "").strip()

                if not email:
                    errors.append(f"Row {row_num}: Email is required")
                    skipped_count += 1
                    continue

                # Check if subscriber already exists
                if NewsletterSubscriber.objects.filter(email__iexact=email).exists():
                    skipped_count += 1
                    continue

                # Create subscriber
                skip_confirmation = request.POST.get("skip_confirmation") == "true"
                try:
                    subscriber = NewsletterSubscriber.objects.create(
                        email=email,
                        language=language if language in ["fr", "en", "es"] else "fr",
                        tags=tags,
                        is_active=True,
                        is_confirmed=skip_confirmation,
                        confirmed_at=timezone.now() if skip_confirmation else None,
                        consent_given_at=timezone.now(),
                    )
                    created_count += 1
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
                    skipped_count += 1

            logger.info(f"CSV import: {created_count} created, {skipped_count} skipped by user {request.user.email}")

            return JsonResponse({
                "success": True,
                "message": str(_("Import completed: %(created)s created, %(skipped)s skipped") % {
                    "created": created_count,
                    "skipped": skipped_count,
                }),
                "created": created_count,
                "skipped": skipped_count,
                "errors": errors[:10],  # Limit to first 10 errors
            })

        except Exception as e:
            logger.error(f"CSV import error: {str(e)}")
            return JsonResponse({
                "success": False,
                "message": str(_("Error processing CSV: %(error)s") % {"error": str(e)}),
            }, status=500)
