"""
Resource document views for dashboard CRUD operations.
"""
import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from tech_articles.resources.models import ResourceDocument
from tech_articles.resources.forms import ResourceDocumentForm

logger = logging.getLogger(__name__)


class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin that requires user to be an admin or staff."""

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


class ResourceListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """List all resource documents with search and filtering."""
    model = ResourceDocument
    template_name = "tech-articles/dashboard/pages/resources/list.html"
    context_object_name = "resources"
    paginate_by = 10
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get("search", "").strip()
        access_level = self.request.GET.get("access_level", "")

        if search:
            queryset = queryset.filter(title__icontains=search)
        if access_level:
            queryset = queryset.filter(access_level=access_level)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "")
        context["access_level"] = self.request.GET.get("access_level", "")
        return context


class ResourceCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    """Create a new resource document."""
    model = ResourceDocument
    form_class = ResourceDocumentForm
    template_name = "tech-articles/dashboard/pages/resources/create.html"
    success_url = reverse_lazy("resources:resources_list")

    def form_valid(self, form):
        messages.success(self.request, _("Resource document created successfully."))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Please correct the errors below."))
        return super().form_invalid(form)


class ResourceUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    """Update an existing resource document."""
    model = ResourceDocument
    form_class = ResourceDocumentForm
    template_name = "tech-articles/dashboard/pages/resources/edit.html"
    success_url = reverse_lazy("resources:resources_list")

    def form_valid(self, form):
        messages.success(self.request, _("Resource document updated successfully."))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Please correct the errors below."))
        return super().form_invalid(form)


class ResourceDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    """Delete a resource document."""
    model = ResourceDocument
    template_name = "tech-articles/dashboard/pages/resources/delete.html"
    success_url = reverse_lazy("resources:resources_list")

    def form_valid(self, form):
        messages.success(self.request, _("Resource document deleted successfully."))
        return super().form_valid(form)
