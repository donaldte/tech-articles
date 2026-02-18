import logging
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from tech_articles.utils.email import EmailUtil
from tech_articles.appointments.models import Appointment

logger = logging.getLogger(__name__)

def send_appointment_confirmation(appointment_id):
    """
    Send a confirmation email to the user when an appointment is booked.
    """
    try:
        appointment = Appointment.objects.select_related('user', 'slot', 'appointment_type').get(id=appointment_id)
        user = appointment.user
        
        subject = _("Appointment Confirmed: {type}").format(type=appointment.appointment_type.name)
        template = "tech-articles/emails/appointment_confirmation.html"
        
        context = {
            "user": user,
            "appointment": appointment,
            "slot": appointment.slot,
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
        
        subject = _("Reminder: Appointment with Runbookly - {date}").format(
            date=appointment.slot.start_at.strftime("%B %d, %Y")
        )
        template = "tech-articles/emails/appointment_reminder.html"
        
        context = {
            "user": user,
            "appointment": appointment,
            "slot": appointment.slot,
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
