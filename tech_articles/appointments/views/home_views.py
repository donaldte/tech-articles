"""
Home appointment views for appointment booking flow.
These are template-only views for the public-facing appointment booking interface.
"""
from django.views.generic import TemplateView


class AppointmentListHomeView(TemplateView):
    """
    Display available appointment time slots in a weekly calendar view.
    Users can browse and select available time slots.
    """
    template_name = "tech-articles/home/pages/appointments/list.html"


class AppointmentDetailHomeView(TemplateView):
    """
    Display appointment details including time, duration, and amount.
    Users can review and confirm the appointment before payment.
    """
    template_name = "tech-articles/home/pages/appointments/detail.html"


class AppointmentPaymentHomeView(TemplateView):
    """
    Payment page for confirmed appointments.
    Final step in the appointment booking flow.
    """
    template_name = "tech-articles/home/pages/appointments/payment.html"
