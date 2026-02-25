"""
Appointment views for dashboard CRUD operations.
"""
import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.views import View
from django.utils import timezone

from tech_articles.appointments.models import Appointment
from tech_articles.appointments.forms import AppointmentForm
from tech_articles.utils.mixins import AdminRequiredMixin

logger = logging.getLogger(__name__)


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

class AppointmentDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    """View appointment details."""
    model = Appointment
    template_name = "tech-articles/dashboard/pages/appointments/detail.html"
    context_object_name = "appointment"


class UpdateMeetingLinkApiView(LoginRequiredMixin, AdminRequiredMixin, View):
    """API view to update meeting link via AJAX."""

    def post(self, request, pk):
        from django.http import JsonResponse
        from tech_articles.utils.enums import AppointmentStatus

        try:
            appointment = Appointment.objects.get(pk=pk)
            meeting_link = request.POST.get("meeting_link")

            if not meeting_link:
                return JsonResponse({"status": "error", "message": _("Meeting link is required.")}, status=400)

            appointment.meeting_link = meeting_link

            # If status was link_pending, move to confirmed
            if appointment.status == AppointmentStatus.LINK_PENDING:
                appointment.status = AppointmentStatus.CONFIRMED
                appointment.confirmed_at = timezone.now()

            appointment.save()

            # Trigger notification to user
            from tech_articles.appointments.tasks.appointment_tasks import send_appointment_link_notification
            send_appointment_link_notification(appointment.id)

            return JsonResponse({
                "status": "success",
                "message": _("Meeting link updated successfully. Appointment confirmed.")
            })
        except Appointment.DoesNotExist:
            return JsonResponse({"status": "error", "message": _("Appointment not found.")}, status=404)
        except Exception as e:
            logger.error(f"Error updating meeting link: {e}")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
