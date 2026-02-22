import logging
import zoneinfo

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView

from tech_articles.appointments.models import AvailabilityRule
from tech_articles.appointments.forms import AvailabilityRuleForm
from tech_articles.utils.mixins import AdminRequiredMixin

from django.http import JsonResponse
from django.views import View
from tech_articles.appointments.models import AvailabilityRule, AppointmentType, AppointmentSlot
from tech_articles.utils.mixins import AdminRequiredMixin

logger = logging.getLogger(__name__)


class AvailabilitySettingsView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """Manage availability settings."""
    template_name = "tech-articles/dashboard/pages/appointments/availability.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["appointment_types"] = AppointmentType.objects.filter(is_active=True)
        return context


class AvailabilityRuleApiView(LoginRequiredMixin, AdminRequiredMixin, View):
    """API endpoint for fetching and managing availability rules and slots."""

    def get(self, request):
        start_date_str = request.GET.get("start")
        end_date_str = request.GET.get("end")

        rules = AvailabilityRule.objects.all()
        rules_data = [
            {
                "id": str(rule.id),
                "weekday": rule.weekday,
                "start_time": rule.start_time.strftime("%H:%M"),
                "end_time": rule.end_time.strftime("%H:%M"),
                "is_active": rule.is_active,
            }
            for rule in rules
        ]

        # Fetch slots if date range is provided
        from django.utils.dateparse import parse_datetime
        from tech_articles.appointments.models import AppointmentSlot

        slots_data = []
        if start_date_str and end_date_str:
            start_date = parse_datetime(start_date_str)
            end_date = parse_datetime(end_date_str)
            if start_date and end_date:
                # 1. Fetch real slots from DB (Manual blocks OR Bookings)
                real_slots = AppointmentSlot.objects.filter(
                    start_at__gte=start_date,
                    start_at__lte=end_date
                ).select_related("appointment")
                
                # 2. Map real slots to our data format
                for slot in real_slots:
                    slots_data.append({
                        "id": str(slot.id),
                        "start_at": slot.start_at.isoformat(),
                        "end_at": slot.end_at.isoformat(),
                        "is_booked": slot.is_booked,
                        "appointment_id": str(slot.appointment.id) if hasattr(slot, 'appointment') else None,
                        "is_virtual": False
                    })
                
                # 3. Add virtual blocks (Free time) from availability_utils
                from tech_articles.appointments.utils.availability_utils import get_available_blocks
                available_blocks = get_available_blocks(start_date.date(), end_date.date())
                
                for block in available_blocks:
                    slots_data.append({
                        "id": block['id'],
                        "start_at": block['start_at'].isoformat(),
                        "end_at": block['end_at'].isoformat(),
                        "is_booked": False,
                        "appointment_id": None,
                        "is_virtual": True
                    })

                # Sort slots by start_at
                slots_data.sort(key=lambda x: x['start_at'])

        return JsonResponse({
            "rules": rules_data,
            "slots": slots_data
        })


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
        self.object = form.save()
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                "status": "success",
                "message": _("Availability rule created successfully."),
                "id": str(self.object.id)
            })
        messages.success(self.request, _("Availability rule created successfully."))
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                "status": "error",
                "errors": form.errors.get_json_data()
            }, status=400)
        messages.error(self.request, _("Please correct the errors below."))
        return super().form_invalid(form)


class AvailabilityRuleUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    """Update an existing availability rule."""
    model = AvailabilityRule
    form_class = AvailabilityRuleForm
    template_name = "tech-articles/dashboard/pages/appointments/availability/edit.html"
    success_url = reverse_lazy("appointments:availability_rules_list")

    def form_valid(self, form):
        self.object = form.save()
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                "status": "success",
                "message": _("Availability rule updated successfully."),
                "id": str(self.object.id)
            })
        messages.success(self.request, _("Availability rule updated successfully."))
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                "status": "error",
                "errors": form.errors.get_json_data()
            }, status=400)
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


class AppointmentSettingsAdminView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """Admin page to configure global appointment settings (e.g. display timezone)."""
    template_name = "tech-articles/dashboard/pages/appointments/settings.html"

    def _get_common_timezones(self):
        try:
            return sorted(zoneinfo.available_timezones())
        except Exception:
            return [
                "Africa/Douala", "Africa/Lagos", "Africa/Nairobi", "Africa/Cairo",
                "Africa/Johannesburg", "America/New_York", "America/Chicago",
                "America/Denver", "America/Los_Angeles", "America/Toronto",
                "America/Sao_Paulo", "Asia/Tokyo", "Asia/Shanghai", "Asia/Kolkata",
                "Asia/Dubai", "Asia/Singapore", "Europe/London", "Europe/Paris",
                "Europe/Berlin", "Europe/Moscow", "Australia/Sydney",
                "Pacific/Auckland", "UTC",
            ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from tech_articles.appointments.models import AppointmentSettings
        context["settings"] = AppointmentSettings.get_settings()
        context["common_timezones"] = self._get_common_timezones()
        return context

    def post(self, request, *args, **kwargs):
        from tech_articles.appointments.models import AppointmentSettings
        timezone_val = request.POST.get("timezone", "UTC").strip()
        all_tz = self._get_common_timezones()
        if timezone_val not in all_tz:
            messages.error(request, _("Invalid timezone selected."))
            return self.get(request, *args, **kwargs)

        settings_obj = AppointmentSettings.get_settings()
        settings_obj.timezone = timezone_val
        settings_obj.save()
        from django.shortcuts import redirect
        from django.urls import reverse
        return redirect(reverse("appointments:appointment_settings"))
