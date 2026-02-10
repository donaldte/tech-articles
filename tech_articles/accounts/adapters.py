from __future__ import annotations

import typing

from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.internal.userkit import user_email
from allauth.core.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.contrib import messages
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

if typing.TYPE_CHECKING:
    from allauth.socialaccount.models import SocialLogin, SocialAccount
    from django.http import HttpRequest, HttpResponseRedirect

    from tech_articles.accounts.models import User


class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request: HttpRequest) -> bool:
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)

    def get_login_redirect_url(self, request: HttpRequest) -> str:
        """
        Returns the URL to redirect to after a successful login.
        Override to ensure we always redirect to home page.
        """
        # Check if there's a 'next' parameter in the request
        if next_url := request.GET.get('next') or request.POST.get('next'):
            return next_url
        # Otherwise, redirect to home page
        return reverse('common:home')


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(
        self,
        request: HttpRequest,
        sociallogin: SocialLogin,
    ) -> bool:
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)

    def populate_user(
        self,
        request: HttpRequest,
        sociallogin: SocialLogin,
        data: dict[str, typing.Any],
    ) -> User:
        """
        Populates user information from social provider info.

        See: https://docs.allauth.org/en/latest/socialaccount/advanced.html#creating-and-populating-user-instances
        """
        user = super().populate_user(request, sociallogin, data)
        if not user.name:
            if name := data.get("name"):
                user.name = name
            elif first_name := data.get("first_name"):
                user.name = first_name
                if last_name := data.get("last_name"):
                    user.name += f" {last_name}"
        return user

    def get_connect_redirect_url(self, request, socialaccount):
        """
        Returns the URL to redirect to after connecting a social account.
        Override to ensure we always redirect to home page.
        """
        # Check if there's a 'next' parameter in the request
        if next_url := request.GET.get('next') or request.POST.get('next'):
            return next_url
        # Otherwise, redirect to home page
        return reverse('common:home')


    def pre_social_login(self, request, sociallogin):
        """
        Handle actions before the social login process.

        This method is called before the social login is processed.
        It can be used to implement custom behavior, such as linking
        a social account to an existing user account based on email.

        Args:
            request: The HTTP request object
            sociallogin: The social login instance
        """
        # If user is already logged in, do nothing (let Allauth handle linking)
        if request.user.is_authenticated:
            return

        email = user_email(sociallogin.user)
        if email:
            try:
                user = User.objects.get(email__iexact=email)
                # If a SocialAccount already exists, do nothing
                if SocialAccount.objects.filter(user=user, provider=sociallogin.account.provider).exists():
                    return

                # Otherwise, link this social account to the existing user
                sociallogin.connect(request, user)

                # Optionally, show a message
                messages.success(request, _("Your social account has been linked to your existing account."))

                # Optionally, force login
                raise ImmediateHttpResponse(HttpResponseRedirect("/"))
            except User.DoesNotExist:
                pass


