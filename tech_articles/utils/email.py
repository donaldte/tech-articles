import logging
import os
from typing import List, Optional

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


class EmailUtil:
    """Email utility class providing static methods for sending emails via Django."""

    @staticmethod
    def send_generic_email(
        subject: str,
        to: List[str],
        _from: str = None,
        file_path: Optional[str] = None,
        html_content: Optional[str] = None,
        text_content: Optional[str] = None,
    ) -> bool:
        """Send a generic email using Django's default email backend."""
        logger.info("## Sending Generic Email ##")
        logger.info(f"Subject: {subject}")
        logger.info(f"To: {to}")
        logger.info(f"From: {_from}")
        logger.info(f"File path: {file_path}")

        # Validate inputs
        if not isinstance(to, list):
            logger.error(f"Invalid 'to' parameter: expected list, got {type(to)}")
            raise ValueError("The 'to' parameter must be a list")
        if not to or None in to or any(not email for email in to):
            logger.error(f"Invalid 'to' list: {to}")
            raise ValueError("The 'to' list must contain valid email addresses")
        if not subject:
            logger.error("Subject is empty")
            raise ValueError("Subject is required")
        if not text_content and not html_content:
            logger.error("Content is empty")
            raise ValueError("Content is required")

        is_debug = getattr(settings, "DEBUG", False)
        if is_debug:
            subject = f"[TEST] {subject}"
            logger.info(f"Debug mode, updated subject: {subject}")

        default_from = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com")
        from_email = _from or default_from
        logger.info(f"Resolved from_email: {from_email}")

        if getattr(settings, "TESTING", False):
            logger.info(
                f"*** TEST EMAIL MODE ***\nContent: {text_content or html_content}\nSubject: {subject}\nTo: {to}\nFrom: {from_email}"
            )
            return True

        return EmailUtil._send_django_email(subject, text_content or html_content, to, from_email, file_path)

    @staticmethod
    def _send_django_email(
        subject: str,
        content: str,
        to: List[str],
        from_email: str,
        file_path: Optional[str],
    ) -> bool:
        """Send email using Django's default email backend."""
        logger.info("## Sending email via Django backend ##")
        try:
            email = EmailMessage(
                subject,
                content,
                from_email,
                [],
                bcc=to,
            )
            email.content_subtype = "html"

            if file_path and os.path.exists(file_path):
                logger.info(f"Attaching file: {file_path}")
                email.attach_file(file_path)
            else:
                if file_path:
                    logger.warning(f"File not found at: {file_path}")

            email.send()
            logger.info("✅ Email sent successfully via Django backend")
            return True

        except Exception as e:
            logger.error(f"❌ Error sending email via Django backend: {e}")
            return False

    @staticmethod
    def send_email_with_template(
        template: str,
        context: dict,
        receivers: list,
        subject: str,
    ) -> bool:
        """Send email using a template."""
        context["subject"] = subject
        body = render_to_string(
            template_name=template,
            context=context,
        )

        try:
            return EmailUtil.send_generic_email(
                subject=subject,
                to=receivers,
                html_content=body,
            )
        except Exception as e:
            logger.error(f"An error occurred while sending email with template: {e}")
            return False
