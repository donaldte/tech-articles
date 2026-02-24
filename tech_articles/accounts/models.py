from __future__ import annotations

from typing import ClassVar

from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.db.models import EmailField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.utils import timezone
from django.contrib.auth.hashers import check_password

from .managers import UserManager
from ..common.models import UUIDModel, TimeStampedModel
from ..utils.enums import UserRole, LanguageChoices


class User(UUIDModel, TimeStampedModel, AbstractUser):
    """
    Default custom user model for tech-articles.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    name = CharField(
        _("name of user"),
        blank=True,
        max_length=255,
        help_text=_("Full name of the user"),
    )
    email = EmailField(
        _("email address"),
        unique=True,
        help_text=_("Unique email address for login"),
    )
    username = None  # type: ignore[assignment]

    role = CharField(
        _("user role"),
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.USER,
        db_index=True,
        help_text=_("Role determining user permissions"),
    )
    preferred_language = CharField(
        _("preferred language"),
        max_length=5,
        choices=LanguageChoices.choices,
        default=LanguageChoices.FR,
        db_index=True,
        help_text=_("User's preferred language for the interface"),
    )
    timezone = CharField(
        _("timezone"),
        max_length=64,
        default="America/Montreal",
        help_text=_("User's timezone for scheduling"),
    )

    avatar = models.ImageField(
        _("avatar"),
        upload_to="avatars/%Y/%m/",
        blank=True,
        null=True,
        help_text=_("Profile picture for the user"),
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects: ClassVar[UserManager] = UserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["-created_at"]

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("accounts:detail", kwargs={"pk": self.id})

    @property
    def first_name(self) -> str:
        # allauth sometimes expects name split; we expose minimal compatibility
        return self.name.split(" ")[0] if self.name else ""

    @property
    def last_name(self) -> str:
        if not self.name or " " not in self.name:
            return ""
        return " ".join(self.name.split(" ")[1:])

    def get_avatar_url(self) -> str:
        """
        Get the URL of the avatar safely.
        Returns the URL if the image exists, otherwise returns an empty string.
        """
        if self.avatar and hasattr(self.avatar, 'url'):
            try:
                return self.avatar.url
            except (ValueError, AttributeError):
                return ""
        return ""

    def __str__(self) -> str:
        return self.email


class OTPVerification(UUIDModel, TimeStampedModel, models.Model):
    """
    One-Time Password (OTP) verification record.

    Stores a hashed OTP code for a given email and purpose (signup/login/password reset),
    tracks attempts and expiry, and records minimal request metadata for auditing.
    """

    class Purpose(models.TextChoices):
        SIGNUP_VERIFICATION = 'signup_verification', _("Signup Verification")
        LOGIN_VERIFICATION = 'login_verification', _("Login Verification")
        PASSWORD_RESET_VERIFICATION = 'password_reset_verification', _(
            "Password Reset Verification"
        )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="otp_verifications",
        help_text=_("User associated with this OTP (nullable until identity confirmed)"),
    )
    email = models.EmailField(
        _("email address"),
        db_index=True,
        help_text=_("Email address for which OTP was generated"),
    )
    code_hash = models.CharField(
        _("OTP code hash"),
        max_length=255,
        help_text=_("Hashed OTP code"),
    )
    purpose = models.CharField(
        _("OTP purpose"),
        max_length=50,
        choices=Purpose.choices,
        db_index=True,
        help_text=_("Purpose of this OTP (signup, login, or password reset)"),
    )
    is_verified = models.BooleanField(
        _("is verified"),
        default=False,
        db_index=True,
        help_text=_("Whether this OTP has been successfully verified"),
    )
    verified_at = models.DateTimeField(
        _("verified at"),
        null=True,
        blank=True,
        help_text=_("Timestamp when OTP was verified"),
    )
    attempts_count = models.IntegerField(
        _("attempts count"),
        default=0,
        help_text=_("Number of verification attempts made"),
    )
    max_attempts = models.IntegerField(
        _("max attempts"),
        default=3,
        help_text=_("Maximum number of verification attempts allowed"),
    )
    expires_at = models.DateTimeField(
        _("expires at"),
        db_index=True,
        help_text=_("Timestamp when OTP expires"),
    )
    ip_address = models.GenericIPAddressField(
        _("IP address"),
        null=True,
        blank=True,
        help_text=_("IP address from which OTP was requested (for audit)"),
    )
    user_agent = models.TextField(
        _("user agent"),
        blank=True,
        help_text=_("User agent from which OTP was requested (for audit)"),
    )

    class Meta:
        verbose_name = _("OTP Verification")
        verbose_name_plural = _("OTP Verifications")
        indexes = [
            models.Index(fields=["email", "purpose", "is_verified", "expires_at"]),
            models.Index(fields=["created_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.email} - {self.purpose}"

    def is_expired(self) -> bool:
        """Return True if this OTP has expired."""
        return timezone.now() > self.expires_at

    def is_valid_code(self, raw_code: str) -> bool:
        """Check if the provided raw code matches the stored hash."""
        return check_password(raw_code, self.code_hash)

    def can_attempt(self) -> bool:
        """Return True if another verification attempt is allowed."""
        return self.attempts_count < self.max_attempts

    def increment_attempts(self) -> None:
        """Increment and persist the attempts counter."""
        self.attempts_count += 1
        self.save(update_fields=["attempts_count"])

    def mark_verified(self) -> None:
        """Mark this OTP as verified and record timestamp."""
        self.is_verified = True
        self.verified_at = timezone.now()
        self.save(update_fields=["is_verified", "verified_at"])

    @classmethod
    def get_valid(cls, email: str, purpose: str) -> "OTPVerification | None":
        """Return the most recent unverified, non-expired OTP for an email/purpose."""
        return cls.objects.filter(
            email__iexact=email,
            purpose=purpose,
            is_verified=False,
            expires_at__gt=timezone.now(),
        ).order_by("-created_at").first()
