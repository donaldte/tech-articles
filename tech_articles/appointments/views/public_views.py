from django.http import JsonResponse
from django.views import View
from django.utils.dateparse import parse_datetime
from tech_articles.appointments.models import AppointmentSlot, AppointmentType
from tech_articles.appointments.utils.slot_generator import generate_virtual_slots_for_range
from decimal import Decimal

class PublicAppointmentSlotsApiView(View):
    """API endpoint for fetching available appointment slots for the public booking flow."""

    def get(self, request):
        start_date_str = request.GET.get("start")
        end_date_str = request.GET.get("end")

        if not start_date_str or not end_date_str:
            return JsonResponse({"error": "Start and end dates are required."}, status=400)

        start_date = parse_datetime(start_date_str)
        end_date = parse_datetime(end_date_str)

        if not start_date or not end_date:
            return JsonResponse({"error": "Invalid date format."}, status=400)

        # 1. Fetch "Real" slots from DB
        real_slots = AppointmentSlot.objects.filter(
            start_at__gte=start_date,
            start_at__lte=end_date,
        )

        # 2. Get frozen dates (any day with a booking)
        frozen_dates = real_slots.filter(is_booked=True).values_list('start_at__date', flat=True).distinct()

        # 3. Generate Virtual slots from rules
        from tech_articles.appointments.utils.slot_generator import generate_virtual_slots_for_range
        virtual_slots = generate_virtual_slots_for_range(start_date.date(), end_date.date())

        # 4. Combine and Filter
        available_slots = []
        
        # Add real slots that are NOT booked and NOT on frozen dates
        for slot in real_slots.filter(is_booked=False).exclude(start_at__date__in=list(frozen_dates)):
            available_slots.append({
                "id": str(slot.id),
                "startTime": slot.start_at.strftime("%H:%M"),
                "endTime": slot.end_at.strftime("%H:%M"),
                "date": slot.start_at.date().isoformat(),
                "duration": (slot.end_at - slot.start_at).total_seconds() / 60,
                "is_virtual": False
            })

        # Add virtual slots that are NOT on frozen dates and don't overlap with existing slots
        # overlapping check is already partially done in generate_virtual_slots_for_range 
        # but let's be double sure and exclude frozen dates
        for vslot in virtual_slots:
            if vslot['start_at'].date() not in frozen_dates:
                # Check if a real slot already exists at this exact time
                already_exists = any(s.start_at == vslot['start_at'] for s in real_slots)
                if not already_exists:
                    available_slots.append({
                        "id": f"v_{vslot['start_at'].isoformat()}", # Virtual ID
                        "startTime": vslot['start_at'].strftime("%H:%M"),
                        "endTime": vslot['end_at'].strftime("%H:%M"),
                        "date": vslot['start_at'].date().isoformat(),
                        "duration": (vslot['end_at'] - vslot['start_at']).total_seconds() / 60,
                        "is_virtual": True
                    })

        # Sort by start time
        available_slots.sort(key=lambda x: (x['date'], x['startTime']))

        return JsonResponse({"slots": available_slots})
