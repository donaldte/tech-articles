import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext as _

from tech_articles.utils.email import EmailUtil

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_otp_email(self, email: str, purpose: str, code: str, otp_id: str):
    """Send OTP email asynchronously. Will retry on failure.

    This task expects templates:
      - tech-articles/home/pages/accounts/email/otp_signup_verification_message.txt / .html
      - tech-articles/home/pages/accounts/email/otp_login_verification_message.txt / .html
      - tech-articles/home/pages/accounts/email/otp_password_reset_verification_message.txt / .html
    """
    try:
        purpose_config = {
            'signup_verification': {
                'template': 'tech-articles/home/pages/accounts/email/otp_signup_verification_message',
                'subject': _('Verify your email address'),
            },
            'login_verification': {
                'template': 'tech-articles/home/pages/accounts/email/otp_login_verification_message',
                'subject': _('Your login code'),
            },
            'password_reset_verification': {
                'template': 'tech-articles/home/pages/accounts/email/otp_password_reset_verification_message',
                'subject': _('Reset your password'),
            },
        }

        config = purpose_config.get(purpose)
        if not config:
            logger.error('Unknown OTP purpose: %s', purpose)
            return False

        context = {
            'code': code,
            'email': email,
            'otp_ttl_minutes': getattr(settings, 'OTP_TTL_SECONDS', 300) // 60,
            'site_name': getattr(settings, 'SITE_NAME', 'Runbookly'),
        }

        html_message = render_to_string(f"{config['template']}.html", context)
        text_message = render_to_string(f"{config['template']}.txt", context)

        EmailUtil.send_generic_email(
            subject=str(config['subject']),
            _from=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
            to=[email],
            html_content=html_message,
            text_content=text_message,
        )

        logger.info('OTP email sent %s -> %s', otp_id, email)
        return True

    except Exception as exc:
        logger.exception('Error sending OTP email %s: %s', otp_id, exc)
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
