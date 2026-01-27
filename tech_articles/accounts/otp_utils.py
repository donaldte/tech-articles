"""
Utilities for OTP generation, hashing, verification, and rate-limiting.

This module is intentionally minimal for the signup flow.
"""
from __future__ import annotations

import secrets
from datetime import timedelta
from typing import Tuple

from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import OTPVerification


class OTPError(Exception):
    pass


class OTPRateLimitExceeded(OTPError):
    pass


class OTPNotFound(OTPError):
    pass


class OTPExpired(OTPError):
    pass


class OTPMaxAttemptsExceeded(OTPError):
    pass


class OTPInvalidCode(OTPError):
    pass


def generate_otp_code(length: int | None = None) -> str:
    length = length or settings.OTP_CODE_LENGTH
    return ''.join(secrets.choice('0123456789') for _ in range(length))


def hash_otp_code(code: str) -> str:
    return make_password(code)


def check_otp_code(raw_code: str, hashed_code: str) -> bool:
    return check_password(raw_code, hashed_code)


def check_rate_limit(email: str) -> Tuple[bool, int]:
    cache_key = f'otp_requests:{email.lower()}'
    current = cache.get(cache_key, 0)
    max_requests = getattr(settings, 'OTP_RATE_LIMIT_MAX_REQUESTS', 3)
    remaining = max(0, max_requests - current)
    is_limited = current >= max_requests
    return is_limited, remaining


def increment_rate_limit(email: str) -> None:
    cache_key = f'otp_requests:{email.lower()}'
    current = cache.get(cache_key, 0)
    cache.set(cache_key, current + 1, getattr(settings, 'OTP_RATE_LIMIT_WINDOW', 60))


def reset_rate_limit(email: str) -> None:
    cache_key = f'otp_requests:{email.lower()}'
    cache.delete(cache_key)


def create_otp(email: str, purpose: str, user=None, ip_address: str | None = None, user_agent: str | None = None) -> OTPVerification:
    # Validate email
    try:
        validate_email(email)
    except ValidationError:
        raise ValidationError(_('Invalid email address'))

    email = email.lower().strip()

    # Rate limit check
    is_limited, __ = check_rate_limit(email)
    if is_limited:
        raise OTPRateLimitExceeded(_('Too many OTP requests. Please try again later.'))

    # Generate and hash code
    code = generate_otp_code()
    code_hash = hash_otp_code(code)

    expires_at = timezone.now() + timedelta(seconds=getattr(settings, 'OTP_TTL_SECONDS', 300))

    otp = OTPVerification.objects.create(
        user=user,
        email=email,
        code_hash=code_hash,
        purpose=purpose,
        expires_at=expires_at,
        ip_address=ip_address,
        user_agent=user_agent,
        max_attempts=getattr(settings, 'OTP_MAX_ATTEMPTS', 3),
    )

    # Enqueue email send (lazy import to avoid import cycles at module import time)
    try:
        from .tasks import send_otp_email

        send_otp_email.delay(email=email, purpose=purpose, code=code, otp_id=str(otp.id))
    except Exception:
        # If Celery not configured, try synchronous send as fallback
        try:
            from .tasks import send_otp_email as send_otp_sync

            send_otp_sync(email=email, purpose=purpose, code=code, otp_id=str(otp.id))
        except Exception:
            # best-effort: don't expose internal errors
            otp.delete()
            raise

    increment_rate_limit(email)
    return otp


def verify_otp(email: str, code: str, purpose: str) -> OTPVerification:
    email = email.lower().strip()
    otp = OTPVerification.get_valid(email, purpose)
    if not otp:
        raise OTPNotFound(_('OTP not found or expired'))

    if otp.is_expired():
        raise OTPExpired(_('OTP has expired. Please request a new one.'))

    if not otp.can_attempt():
        raise OTPMaxAttemptsExceeded(_('Too many verification attempts. Please request a new OTP.'))

    otp.increment_attempts()

    if not otp.is_valid_code(code):
        raise OTPInvalidCode(_('Invalid OTP code. Please try again.'))

    otp.mark_verified()
    # reset rate limit on success
    reset_rate_limit(email)
    return otp
