from django.http import JsonResponse
from django.views import View
from django.utils.dateparse import parse_datetime
from tech_articles.appointments.models import AppointmentSlot, AppointmentType
from decimal import Decimal

class PublicAppointmentSlotsApiView(View):
    """API endpoint for fetching available appointment slots for the public booking flow."""

    def get(self, request):
        start_date_str = request.GET.get("start")
        end_date_str = request.GET.get("end")

        if not start_date_str or not end_date_str:
            return JsonResponse({"error": "Start and end dates are required."}, status=400)

        from django.utils.dateparse import parse_datetime
        start_date = parse_datetime(start_date_str)
        end_date = parse_datetime(end_date_str)

        if not start_date or not end_date:
            return JsonResponse({"error": "Invalid date format."}, status=400)

        # Use the logic from availability_utils
        from tech_articles.appointments.utils.availability_utils import get_available_blocks
        available_slots = get_available_blocks(start_date.date(), end_date.date())

        # The frontend expects 'slots' key
        return JsonResponse({"slots": available_slots})
