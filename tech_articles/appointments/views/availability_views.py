"""
Availability rule views for dashboard CRUD operations.
"""
import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView

from tech_articles.appointments.models import AvailabilityRule
from tech_articles.appointments.forms import AvailabilityRuleForm
from tech_articles.utils.mixins import AdminRequiredMixin

logger = logging.getLogger(__name__)



class AvailabilitySettingsView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """Manage availability settings."""
    template_name = "tech-articles/dashboard/pages/appointments/availability.html"


class AvailabilityRuleListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """List all availability rules."""
    model = AvailabilityRule
    template_name = "tech-articles/dashboard/pages/appointments/availability/list.html"
    context_object_name = "availability_rules"
    paginate_by = 10
    ordering = ["weekday", "start_time"]

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get("status", "")

        if status == "active":
            queryset = queryset.filter(is_active=True)
        elif status == "inactive":
            queryset = queryset.filter(is_active=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status"] = self.request.GET.get("status", "")
        return context


class AvailabilityRuleCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    """Create a new availability rule."""
    model = AvailabilityRule
    form_class = AvailabilityRuleForm
    template_name = "tech-articles/dashboard/pages/appointments/availability/create.html"
    success_url = reverse_lazy("appointments:availability_rules_list")

    def form_valid(self, form):
        messages.success(self.request, _("Availability rule created successfully."))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Please correct the errors below."))
        return super().form_invalid(form)


class AvailabilityRuleUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    """Update an existing availability rule."""
    model = AvailabilityRule
    form_class = AvailabilityRuleForm
    template_name = "tech-articles/dashboard/pages/appointments/availability/edit.html"
    success_url = reverse_lazy("appointments:availability_rules_list")

    def form_valid(self, form):
        messages.success(self.request, _("Availability rule updated successfully."))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Please correct the errors below."))
        return super().form_invalid(form)


class AvailabilityRuleDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    """Delete an availability rule."""
    model = AvailabilityRule
    template_name = "tech-articles/dashboard/pages/appointments/availability/delete.html"
    success_url = reverse_lazy("appointments:availability_rules_list")

    def form_valid(self, form):
        messages.success(self.request, _("Availability rule deleted successfully."))
        return super().form_valid(form)
