"""
Appointment views for dashboard CRUD operations.
"""
import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from tech_articles.appointments.models import Appointment
from tech_articles.appointments.forms import AppointmentForm

logger = logging.getLogger(__name__)


class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin that requires user to be an admin or staff."""

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


class AppointmentListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """List all appointments (admin view)."""
    model = Appointment
    template_name = "tech-articles/dashboard/pages/appointments/list.html"
    context_object_name = "appointments"
    paginate_by = 10
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get("status", "")
        payment_status = self.request.GET.get("payment_status", "")

        if status:
            queryset = queryset.filter(status=status)
        if payment_status:
            queryset = queryset.filter(payment_status=payment_status)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status"] = self.request.GET.get("status", "")
        context["payment_status"] = self.request.GET.get("payment_status", "")
        return context


class AppointmentCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    """Create a new appointment."""
    model = Appointment
    form_class = AppointmentForm
    template_name = "tech-articles/dashboard/pages/appointments/create.html"
    success_url = reverse_lazy("appointments:appointments_list")

    def form_valid(self, form):
        messages.success(self.request, _("Appointment created successfully."))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Please correct the errors below."))
        return super().form_invalid(form)


class AppointmentUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    """Update an existing appointment."""
    model = Appointment
    form_class = AppointmentForm
    template_name = "tech-articles/dashboard/pages/appointments/edit.html"
    success_url = reverse_lazy("appointments:appointments_list")

    def form_valid(self, form):
        messages.success(self.request, _("Appointment updated successfully."))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Please correct the errors below."))
        return super().form_invalid(form)


class AppointmentDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    """View appointment details."""
    model = Appointment
    template_name = "tech-articles/dashboard/pages/appointments/detail.html"
    context_object_name = "appointment"


class AppointmentDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    """Delete an appointment."""
    model = Appointment
    template_name = "tech-articles/dashboard/pages/appointments/delete.html"
    success_url = reverse_lazy("appointments:appointments_list")

    def form_valid(self, form):
        messages.success(self.request, _("Appointment deleted successfully."))
        return super().form_valid(form)
