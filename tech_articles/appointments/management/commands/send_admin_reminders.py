import logging
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.cache import cache
from tech_articles.appointments.models import Appointment
from tech_articles.appointments.tasks.appointment_tasks import send_admin_reminder_email
from tech_articles.utils.enums import AppointmentStatus

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Send reminder emails to admins for upcoming appointments (30 min before)."

    def handle(self, *args, **options):
        now = timezone.now()
        thirty_minutes_from_now = now + timedelta(minutes=30)
        
        # Look for appointments starting in the next ~30 minutes
        # We use a window to be safe (e.g., between 25 and 35 minutes from now)
        start_range = thirty_minutes_from_now - timedelta(minutes=5)
        end_range = thirty_minutes_from_now + timedelta(minutes=5)
        
        appointments = Appointment.objects.filter(
            slot__start_at__gte=start_range,
            slot__start_at__lte=end_range,
            status=AppointmentStatus.CONFIRMED,
        )
        
        count = 0
        for appointment in appointments:
            cache_key = f"admin_reminder_sent_{appointment.id}"
            if cache.get(cache_key):
                continue

            try:
                success = send_admin_reminder_email(appointment.id)
                if success:
                    # Mark as sent in cache for 1 hour to prevent re-sending
                    cache.set(cache_key, True, 3600)
                    count += 1
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Error sending reminder for appointment {appointment.id}: {e}"))
        
        if count > 0:
            self.stdout.write(self.style.SUCCESS(f"Successfully sent {count} admin reminders."))
        else:
            self.stdout.write("No reminders to send at this time.")
