import logging
import zoneinfo
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from tech_articles.utils.email import EmailUtil
from tech_articles.appointments.models import Appointment, AppointmentSettings

logger = logging.getLogger(__name__)

def get_formatted_time(dt, tz_name="UTC"):
    """
    Format a datetime object into a human-readable string in the given timezone.
    """
    try:
        # Convert to target timezone
        tz = zoneinfo.ZoneInfo(tz_name)
        dt_localized = dt.astimezone(tz)
        
        # Format: "Monday, February 22, 2026 at 14:30"
        return dt_localized.strftime("%A, %B %d, %Y " + _("at") + " %H:%M")
    except Exception as e:
        logger.error(f"Error formatting time with timezone {tz_name}: {e}")
        return dt.strftime("%Y-%m-%d %H:%M")

def send_appointment_confirmation(appointment_id):
    """
    Send a confirmation email to the user when an appointment is booked.
    """
    try:
        appointment = Appointment.objects.select_related('user', 'slot', 'appointment_type').get(id=appointment_id)
        user = appointment.user
        
        # Get settings for timezone
        app_settings = AppointmentSettings.get_settings()
        tz_name = app_settings.timezone
        
        formatted_time = get_formatted_time(appointment.slot.start_at, tz_name)
        
        subject = _("Appointment Confirmed: {type}").format(type=appointment.appointment_type.name)
        template = "tech-articles/emails/appointment_confirmation.html"
        
        context = {
            "user": user,
            "appointment": appointment,
            "slot": appointment.slot,
            "formatted_time": formatted_time,
            "timezone": tz_name,
            "site_url": settings.SITE_URL,
        }
        
        success = EmailUtil.send_email_with_template(
            template=template,
            context=context,
            receivers=[user.email],
            subject=subject
        )
        
        if success:
            logger.info(f"Confirmation email sent to {user.email} for appointment {appointment_id}")
        else:
            logger.error(f"Failed to send confirmation email for appointment {appointment_id}")
            
        return success
    except Appointment.DoesNotExist:
        logger.error(f"Appointment {appointment_id} not found for confirmation email")
        return False
    except Exception as e:
        logger.error(f"Error in send_appointment_confirmation: {e}")
        return False

def send_appointment_reminder(appointment_id):
    """
    Send a reminder email to the user before the appointment.
    """
    try:
        appointment = Appointment.objects.select_related('user', 'slot', 'appointment_type').get(id=appointment_id)
        user = appointment.user
        
        app_settings = AppointmentSettings.get_settings()
        tz_name = app_settings.timezone
        
        formatted_time = get_formatted_time(appointment.slot.start_at, tz_name)
        
        subject = _("Reminder: Appointment with Runbookly - {date}").format(
            date=appointment.slot.start_at.strftime("%B %d, %Y")
        )
        template = "tech-articles/emails/appointment_reminder.html"
        
        context = {
            "user": user,
            "appointment": appointment,
            "slot": appointment.slot,
            "formatted_time": formatted_time,
            "timezone": tz_name,
            "site_url": settings.SITE_URL,
        }
        
        success = EmailUtil.send_email_with_template(
            template=template,
            context=context,
            receivers=[user.email],
            subject=subject
        )
        
        return success
    except Exception as e:
        logger.error(f"Error in send_appointment_reminder: {e}")
        return False

def send_appointment_link_notification(appointment_id):
    """
    Notify the user that a meeting link has been added to their appointment.
    """
    try:
        appointment = Appointment.objects.select_related('user', 'slot', 'appointment_type').get(id=appointment_id)
        user = appointment.user
        
        app_settings = AppointmentSettings.get_settings()
        tz_name = app_settings.timezone
        
        formatted_time = get_formatted_time(appointment.slot.start_at, tz_name)
        
        subject = _("Meeting Link Added: {type}").format(type=appointment.appointment_type.name)
        template = "tech-articles/emails/appointment_link_added.html"
        
        context = {
            "user": user,
            "appointment": appointment,
            "slot": appointment.slot,
            "formatted_time": formatted_time,
            "timezone": tz_name,
            "site_url": settings.SITE_URL,
            "meeting_link": appointment.meeting_link
        }
        
        success = EmailUtil.send_email_with_template(
            template=template,
            context=context,
            receivers=[user.email],
            subject=subject
        )
        
        if success:
            logger.info(f"Link notification email sent to {user.email} for appointment {appointment_id}")
        return success
    except Exception as e:
        logger.error(f"Error in send_appointment_link_notification: {e}")
        return False

def send_admin_reminder_email(appointment_id):
    """
    Send a reminder email to the admin before an appointment.
    """
    try:
        appointment = Appointment.objects.select_related('user', 'slot', 'appointment_type').get(id=appointment_id)
        
        app_settings = AppointmentSettings.get_settings()
        tz_name = app_settings.timezone
        
        formatted_time = get_formatted_time(appointment.slot.start_at, tz_name)
        
        subject = _("Admin Reminder: Appointment with {user} - {time}").format(
            user=appointment.user.get_full_name() or appointment.user.username,
            time=formatted_time
        )
        template = "tech-articles/emails/appointment_admin_reminder.html"
        
        context = {
            "appointment": appointment,
            "slot": appointment.slot,
            "formatted_time": formatted_time,
            "timezone": tz_name,
            "site_url": settings.SITE_URL,
        }
        
        # Get all users with staff or superuser status
        from django.contrib.auth import get_user_model
        from django.db.models import Q
        User = get_user_model()
        admins = User.objects.filter(
            Q(is_staff=True) | Q(is_superuser=True),
            is_active=True
        )
        admin_emails = [admin.email for admin in admins if admin.email]
        
        if not admin_emails:
            logger.warning("No admin emails found to send reminder.")
            return False
        
        success = EmailUtil.send_email_with_template(
            template=template,
            context=context,
            receivers=admin_emails,
            subject=subject
        )
        
        if success:
            logger.info(f"Admin reminder email sent to {len(admin_emails)} admins for appointment {appointment_id}")
        return success
    except Exception as e:
        logger.error(f"Error in send_admin_reminder_email: {e}")
        return False
