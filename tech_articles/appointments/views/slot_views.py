"""
Appointment slot views for dashboard CRUD operations.
"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, CreateView, DeleteView

from tech_articles.appointments.models import AppointmentSlot
from tech_articles.appointments.forms.slot_forms import AppointmentSlotForm
from tech_articles.utils.mixins import AdminRequiredMixin


class AppointmentSlotListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """List specific slots for manual management."""
    model = AppointmentSlot
    template_name = "tech-articles/dashboard/pages/appointments/slots/list.html"
    context_object_name = "slots"
    paginate_by = 20
    ordering = ["-start_at"]

    def get_queryset(self):
        return super().get_queryset()


from django.http import JsonResponse
from tech_articles.appointments.forms.slot_forms import AppointmentSlotForm

class AppointmentSlotCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    """Manually create a specific appointment slot."""
    model = AppointmentSlot
    form_class = AppointmentSlotForm
    template_name = "tech-articles/dashboard/pages/appointments/slots/create.html"
    success_url = reverse_lazy("appointments:appointment_slots_list")

    def form_valid(self, form):
        self.object = form.save()
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': _("Appointment slot created successfully.")
            })
        messages.success(self.request, _("Appointment slot created successfully."))
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            errors = form.errors.get_json_data()
            return JsonResponse({
                'status': 'error',
                'errors': errors,
                'message': _("Please correct the errors below.")
            }, status=400)
        return super().form_invalid(form)


class AppointmentSlotDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    """Delete a specific appointment slot."""
    model = AppointmentSlot
    template_name = "tech-articles/dashboard/pages/appointments/slots/delete.html"
    success_url = reverse_lazy("appointments:appointment_slots_list")

    def form_valid(self, form):
        messages.success(self.request, _("Appointment slot deleted successfully."))
        return super().form_valid(form)
