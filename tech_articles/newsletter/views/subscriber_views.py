"""
Newsletter subscriber views for dashboard CRUD operations.
"""
import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from tech_articles.newsletter.models import NewsletterSubscriber
from tech_articles.newsletter.forms import NewsletterSubscriberForm

logger = logging.getLogger(__name__)


class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin that requires user to be an admin or staff."""

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


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

        if search:
            queryset = queryset.filter(email__icontains=search)
        if status == "active":
            queryset = queryset.filter(is_active=True)
        elif status == "inactive":
            queryset = queryset.filter(is_active=False)
        if confirmed == "yes":
            queryset = queryset.filter(is_confirmed=True)
        elif confirmed == "no":
            queryset = queryset.filter(is_confirmed=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "")
        context["status"] = self.request.GET.get("status", "")
        context["confirmed"] = self.request.GET.get("confirmed", "")
        return context


class SubscriberCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    """Create a new newsletter subscriber."""
    model = NewsletterSubscriber
    form_class = NewsletterSubscriberForm
    template_name = "tech-articles/dashboard/pages/newsletter/subscribers/create.html"
    success_url = reverse_lazy("newsletter:subscribers_list")

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
