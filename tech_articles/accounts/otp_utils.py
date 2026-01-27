"""
Utilities for OTP generation, hashing, verification, and rate-limiting.

This module provides secure OTP handling with session-bound tokens
to prevent email enumeration and session hijacking attacks.
"""
from __future__ import annotations

import secrets
import hashlib
import hmac
from datetime import timedelta
from typing import Tuple, Optional, Dict, Any

from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import OTPVerification


# =============================================================================
# Exceptions
# =============================================================================

class OTPError(Exception):
    """Base exception for OTP-related errors."""
    pass


class OTPRateLimitExceeded(OTPError):
    """Raised when too many OTP requests have been made."""
    pass


class OTPNotFound(OTPError):
    """Raised when no valid OTP is found."""
    pass


class OTPExpired(OTPError):
    """Raised when the OTP has expired."""
    pass


class OTPMaxAttemptsExceeded(OTPError):
    """Raised when maximum verification attempts have been exceeded."""
    pass


class OTPInvalidCode(OTPError):
    """Raised when the provided OTP code is invalid."""
    pass


class OTPSessionError(OTPError):
    """Raised when session validation fails."""
    pass


class OTPSessionExpired(OTPSessionError):
    """Raised when the OTP session token has expired."""
    pass


class OTPSessionInvalid(OTPSessionError):
    """Raised when the OTP session token is invalid or tampered."""
    pass


# =============================================================================
# Session Token Management (Secure approach)
# =============================================================================

# Session keys for different OTP purposes
SESSION_KEYS = {
    'signup_verification': '_otp_signup_session',
    'login_verification': '_otp_login_session',
    'password_reset_verification': '_otp_password_reset_session',
}


def _get_session_key(purpose: str) -> str:
    """Get the session key for a given OTP purpose."""
    return SESSION_KEYS.get(purpose, f'_otp_{purpose}_session')


def generate_session_token() -> str:
    """
    Generate a cryptographically secure random token.
    Uses 32 bytes (256 bits) of randomness for strong security.
    """
    return secrets.token_urlsafe(32)


def create_otp_session(request, email: str, purpose: str, otp_id: str) -> str:
    """
    Create a secure OTP session bound to the current request session.

    This stores the OTP context in the server-side session, preventing
    attackers from manipulating email or OTP references via URL/form params.

    Args:
        request: Django HTTP request object
        email: The email address for OTP verification
        purpose: The OTP purpose (signup, login, password_reset)
        otp_id: The UUID of the OTPVerification record

    Returns:
        A signed session token for additional verification
    """
    session_key = _get_session_key(purpose)
    session_token = generate_session_token()

    # Create a fingerprint of the session for additional security
    session_fingerprint = _create_session_fingerprint(request)

    # Store OTP context in session (server-side, not exposed to client)
    request.session[session_key] = {
        'email': email.lower().strip(),
        'otp_id': otp_id,
        'token': session_token,
        'fingerprint': session_fingerprint,
        'created_at': timezone.now().isoformat(),
    }

    # Sign the token with Django's cryptographic signer
    signer = TimestampSigner(salt=f'otp-{purpose}')
    signed_token = signer.sign(session_token)

    return signed_token


def validate_otp_session(request, purpose: str, signed_token: Optional[str] = None) -> Dict[str, Any]:
    """
    Validate and retrieve the OTP session data.

    This ensures the verification request comes from the same session
    that initiated the OTP process.

    Args:
        request: Django HTTP request object
        purpose: The OTP purpose to validate
        signed_token: Optional signed token for additional verification

    Returns:
        Dict containing email, otp_id, and other session data

    Raises:
        OTPSessionError: If session validation fails
    """
    session_key = _get_session_key(purpose)
    session_data = request.session.get(session_key)

    if not session_data:
        raise OTPSessionInvalid(_('No active verification session. Please start the process again.'))

    # Validate session fingerprint (basic session binding)
    current_fingerprint = _create_session_fingerprint(request)
    stored_fingerprint = session_data.get('fingerprint', '')

    if not hmac.compare_digest(current_fingerprint, stored_fingerprint):
        # Fingerprint mismatch could indicate session hijacking
        clear_otp_session(request, purpose)
        raise OTPSessionInvalid(_('Session validation failed. Please start the process again.'))

    # If signed token provided, validate it
    if signed_token:
        try:
            signer = TimestampSigner(salt=f'otp-{purpose}')
            # Max age matches OTP TTL (default 5 minutes)
            max_age = getattr(settings, 'OTP_TTL_SECONDS', 300)
            unsigned_token = signer.unsign(signed_token, max_age=max_age)

            if not hmac.compare_digest(unsigned_token, session_data.get('token', '')):
                raise OTPSessionInvalid(_('Invalid session token.'))

        except SignatureExpired:
            clear_otp_session(request, purpose)
            raise OTPSessionExpired(_('Verification session has expired. Please start again.'))
        except BadSignature:
            clear_otp_session(request, purpose)
            raise OTPSessionInvalid(_('Invalid session token. Please start again.'))

    return session_data


def clear_otp_session(request, purpose: str) -> None:
    """
    Clear the OTP session data after successful verification or on error.
    """
    session_key = _get_session_key(purpose)
    if session_key in request.session:
        del request.session[session_key]


def _create_session_fingerprint(request) -> str:
    """
    Create a fingerprint of the session based on stable request attributes.

    This helps detect potential session hijacking by binding the OTP
    session to certain client characteristics.

    Note: We use only stable attributes that won't change during normal use.
    IP can change (mobile networks), so we don't include it strictly.
    """
    user_agent = request.META.get('HTTP_USER_AGENT', '')

    # Create a hash of the user agent (stable across requests)
    fingerprint_data = f"{user_agent}"
    return hashlib.sha256(fingerprint_data.encode()).hexdigest()[:32]


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
