"""
Newsletter campaign views for dashboard CRUD operations.
"""
import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from tech_articles.newsletter.models import NewsletterCampaign
from tech_articles.newsletter.forms import NewsletterCampaignForm

logger = logging.getLogger(__name__)


class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin that requires user to be an admin or staff."""

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


class CampaignListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """List all newsletter campaigns."""
    model = NewsletterCampaign
    template_name = "tech-articles/dashboard/pages/newsletter/campaigns/list.html"
    context_object_name = "campaigns"
    paginate_by = 10
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get("search", "").strip()
        status = self.request.GET.get("status", "")

        if search:
            queryset = queryset.filter(name__icontains=search)
        if status == "active":
            queryset = queryset.filter(is_active=True)
        elif status == "inactive":
            queryset = queryset.filter(is_active=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "")
        context["status"] = self.request.GET.get("status", "")
        return context


class CampaignCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    """Create a new newsletter campaign."""
    model = NewsletterCampaign
    form_class = NewsletterCampaignForm
    template_name = "tech-articles/dashboard/pages/newsletter/campaigns/create.html"
    success_url = reverse_lazy("newsletter:campaigns_list")

    def form_valid(self, form):
        messages.success(self.request, _("Campaign created successfully."))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Please correct the errors below."))
        return super().form_invalid(form)


class CampaignUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    """Update an existing newsletter campaign."""
    model = NewsletterCampaign
    form_class = NewsletterCampaignForm
    template_name = "tech-articles/dashboard/pages/newsletter/campaigns/edit.html"
    success_url = reverse_lazy("newsletter:campaigns_list")

    def form_valid(self, form):
        messages.success(self.request, _("Campaign updated successfully."))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Please correct the errors below."))
        return super().form_invalid(form)


class CampaignDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    """Delete a newsletter campaign."""
    model = NewsletterCampaign
    template_name = "tech-articles/dashboard/pages/newsletter/campaigns/delete.html"
    success_url = reverse_lazy("newsletter:campaigns_list")

    def form_valid(self, form):
        messages.success(self.request, _("Campaign deleted successfully."))
        return super().form_valid(form)
