"""
Appointment type views for dashboard CRUD operations.
"""
import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from tech_articles.appointments.models import AppointmentType
from tech_articles.appointments.forms import AppointmentTypeForm

logger = logging.getLogger(__name__)


class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin that requires user to be an admin or staff."""

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


class AppointmentTypeListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """List all appointment types with search and filtering."""
    model = AppointmentType
    template_name = "tech-articles/dashboard/pages/appointments/types/list.html"
    context_object_name = "appointment_types"
    paginate_by = 10
    ordering = ["name"]

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


class AppointmentTypeCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    """Create a new appointment type."""
    model = AppointmentType
    form_class = AppointmentTypeForm
    template_name = "tech-articles/dashboard/pages/appointments/types/create.html"
    success_url = reverse_lazy("appointments:appointment_types_list")

    def form_valid(self, form):
        messages.success(self.request, _("Appointment type created successfully."))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Please correct the errors below."))
        return super().form_invalid(form)


class AppointmentTypeUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    """Update an existing appointment type."""
    model = AppointmentType
    form_class = AppointmentTypeForm
    template_name = "tech-articles/dashboard/pages/appointments/types/edit.html"
    success_url = reverse_lazy("appointments:appointment_types_list")

    def form_valid(self, form):
        messages.success(self.request, _("Appointment type updated successfully."))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Please correct the errors below."))
        return super().form_invalid(form)


class AppointmentTypeDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    """Delete an appointment type."""
    model = AppointmentType
    template_name = "tech-articles/dashboard/pages/appointments/types/delete.html"
    success_url = reverse_lazy("appointments:appointment_types_list")

    def form_valid(self, form):
        messages.success(self.request, _("Appointment type deleted successfully."))
        return super().form_valid(form)
