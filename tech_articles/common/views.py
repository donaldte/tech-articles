import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from tech_articles.billing.models import Plan
from tech_articles.content.models import FeaturedArticles, Course

logger = logging.getLogger(__name__)


class HomePageView(TemplateView):
    """
    Home page view that displays featured articles, categories, and popular tags.

    This view uses class-based view (CBV) for better organization and reusability.
    It retrieves and filters content based on publication status and active state.
    Featured articles are retrieved from the FeaturedArticles configuration model.
    """

    template_name = "tech-articles/home/pages/index.html"

    def get_context_data(self, **kwargs):
        """Add active plans and featured articles to context."""
        context = super().get_context_data(**kwargs)
        context["active_plans"] = Plan.objects.filter(is_active=True).prefetch_related(
            "plan_features"
        )

        # Get featured articles from cache helper (ensures singleton and prefetch)
        try:
            featured_map = FeaturedArticles.get_featured_articles_from_cache()
        except Exception:
            featured_map = {"first": None, "second": None, "third": None}

        context["first_featured_article"] = featured_map.get("first")
        context["second_featured_article"] = featured_map.get("second")
        context["third_featured_article"] = featured_map.get("third")

        # Add featured courses (most recent active ones)
        context["featured_courses"] = Course.objects.filter(is_active=True).order_by(
            "-created_at"
        )[:3]

        return context


class AppointmentListHomeView(TemplateView):
    """
    Display available appointment time slots in a weekly calendar view.
    Users can browse and select available time slots.
    """

    template_name = "tech-articles/home/pages/appointments/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from tech_articles.appointments.models import AppointmentSettings

        context["appointment_settings"] = AppointmentSettings.get_settings()
        return context


class AppointmentDetailHomeView(LoginRequiredMixin, TemplateView):
    """
    Display appointment details including time, duration, and amount.
    Users can review and confirm the appointment before payment.
    On POST, creates a pending PaymentTransaction and redirects to the real
    billing checkout (AppointmentPaymentSummaryView).
    """

    template_name = "tech-articles/home/pages/appointments/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slot_id = self.kwargs.get("slot_id")
        from tech_articles.appointments.models import Appointment

        # In this context, we expect an Appointment to exist for the slot
        try:
            appointment = Appointment.objects.select_related(
                "slot", "appointment_type"
            ).get(slot_id=slot_id)
            context["appointment"] = appointment
        except Appointment.DoesNotExist:
            context["appointment"] = None

        from tech_articles.appointments.models import AppointmentSettings

        context["appointment_settings"] = AppointmentSettings.get_settings()

        return context

    def post(self, request, *args, **kwargs):
        from django.shortcuts import get_object_or_404, redirect
        from django.urls import reverse
        from django.contrib import messages
        from tech_articles.appointments.models import Appointment
        from tech_articles.billing.services import AppointmentPaymentService
        from tech_articles.utils.enums import PaymentProvider

        slot_id = self.kwargs.get("slot_id")
        appointment = get_object_or_404(Appointment, slot_id=slot_id, user=request.user)

        try:
            payment_txn = AppointmentPaymentService.initiate_payment(
                appointment=appointment,
                provider=PaymentProvider.STRIPE,
            )
        except ValueError as exc:
            messages.error(request, str(exc))
            return redirect(request.path)
        except Exception as exc:
            logger.exception("Error initiating appointment payment: %s", exc)
            messages.error(request, str(_("An error occurred. Please try again.")))
            return redirect(request.path)

        return redirect(
            reverse(
                "billing:appointment_payment_summary",
                kwargs={"transaction_id": str(payment_txn.id)},
            )
        )


class AppointmentServiceSelectionView(LoginRequiredMixin, TemplateView):
    """
    New professional page for selecting service type and duration.
    """

    template_name = "tech-articles/home/pages/appointments/service_selection.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from tech_articles.appointments.models import AppointmentType
        from django.utils.dateparse import parse_datetime

        start_at_str = self.request.GET.get("start")
        end_at_str = self.request.GET.get("end")

        start_at = parse_datetime(start_at_str) if start_at_str else None
        end_at = parse_datetime(end_at_str) if end_at_str else None

        block_duration_mins = 0
        if start_at and end_at:
            block_duration_mins = (end_at - start_at).total_seconds() / 60

        services = AppointmentType.objects.filter(is_active=True)
        processed_services = []

        for service in services:
            # Parse allowed durations
            durations = [
                int(d.strip())
                for d in service.allowed_durations_minutes.split(",")
                if d.strip().isdigit()
            ]
            # Filter durations that fit in the block
            available_durations = [d for d in durations if d <= block_duration_mins]

            processed_services.append(
                {
                    "obj": service,
                    "available_durations": available_durations,
                    "has_available_duration": len(available_durations) > 0,
                    "durations_display": durations,  # Original for reference
                }
            )

        context.update(
            {
                "services": processed_services,
                "start_at": start_at,
                "end_at": end_at,
                "block_duration": block_duration_mins,
            }
        )
        return context

    def post(self, request, *args, **kwargs):
        from tech_articles.appointments.models import (
            Appointment,
            AppointmentSlot,
            AppointmentType,
        )
        from tech_articles.utils.enums import AppointmentStatus, PaymentStatus
        from django.utils.dateparse import parse_datetime
        from datetime import timedelta
        from django.urls import reverse
        from django.http import HttpResponseRedirect
        from django.contrib import messages
        from django.utils.translation import gettext as _
        from decimal import Decimal

        start_at_str = request.POST.get("start_at")
        service_id = request.POST.get("service_id")
        duration = request.POST.get("duration")

        if not all([start_at_str, service_id, duration]):
            messages.error(request, _("Please select a service and duration."))
            return self.get(request, *args, **kwargs)

        dt = parse_datetime(start_at_str)
        service = AppointmentType.objects.get(id=service_id)
        duration_mins = int(duration)
        end_dt = dt + timedelta(minutes=duration_mins)

        # 1. Create/Check Slot
        # Important: Since we support dynamic blocks, we check if this specific range overlaps with any booked slot
        conflicting = AppointmentSlot.objects.filter(
            Q(
                Q(is_booked=True)
                & Q(
                    appointment__payment_status__in=[
                        PaymentStatus.SUCCEEDED,
                        PaymentStatus.FREE_ACCEPTED,
                    ]
                )
            ),
            start_at__lt=end_dt,
            end_at__gt=dt,
        ).exists()

        if conflicting:
            messages.error(
                request,
                _(
                    "This time range is already partially booked. Please choose another."
                ),
            )
            return HttpResponseRedirect(reverse("common:appointments_book"))

        # Create the materialized slot
        slot = AppointmentSlot.objects.create(
            start_at=dt, end_at=end_dt, is_booked=True, booked_at=timezone.now()
        )

        # 2. Create Appointment
        hourly_rate = service.base_hourly_rate
        total_amount = (hourly_rate * Decimal(duration_mins)) / Decimal(60)

        Appointment.objects.create(
            user=request.user,
            slot=slot,
            appointment_type=service,
            duration_minutes=duration_mins,
            hourly_rate=hourly_rate,
            total_amount=total_amount,
            currency=service.currency,
            status=AppointmentStatus.PENDING,
            payment_status=PaymentStatus.PENDING,
        )

        return HttpResponseRedirect(
            reverse("common:appointments_book_detail", kwargs={"slot_id": str(slot.id)})
        )
