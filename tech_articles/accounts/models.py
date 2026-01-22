from __future__ import annotations

from typing import ClassVar

from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.db.models import EmailField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

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

    avatar_key = CharField(
        _("avatar key"),
        max_length=512,
        blank=True,
        default="",
        help_text=_("S3 key/path for user avatar"),
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

    def __str__(self) -> str:
        return self.email
