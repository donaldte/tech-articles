"""
Profile views for user self-management.
Views for editing profile, security settings, and avatar management.
"""
import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import UpdateView, FormView

from tech_articles.accounts.models import User
from tech_articles.accounts.forms import (
    ProfileEditForm,
    ProfileAvatarForm,
    ProfilePasswordChangeForm,
)

logger = logging.getLogger(__name__)


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """Edit user profile."""
    model = User
    form_class = ProfileEditForm
    template_name = "tech-articles/dashboard/pages/profile/edit.html"
    success_url = reverse_lazy("dashboard:profile_edit")

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Edit Profile")
        context["avatar_form"] = ProfileAvatarForm()
        context["avatar_url"] = self.request.user.get_avatar_url()
        return context

    def form_valid(self, form):
        messages.success(self.request, _("Profile updated successfully."))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Please correct the errors below."))
        return super().form_invalid(form)


class ProfileSecurityView(LoginRequiredMixin, FormView):
    """Security settings - password change."""
    form_class = ProfilePasswordChangeForm
    template_name = "tech-articles/dashboard/pages/profile/security.html"
    success_url = reverse_lazy("accounts:account_login")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Security Settings")
        return context

    def form_valid(self, form):
        form.save()
        messages.success(
            self.request,
            _("Your password has been changed. Please sign in with your new password.")
        )
        # Logout user after password change
        from django.contrib.auth import logout
        logout(self.request)
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Please correct the errors below."))
        return super().form_invalid(form)


class ProfileAvatarUploadView(LoginRequiredMixin, View):
    """Handle avatar upload via AJAX."""

    def post(self, request):
        form = ProfileAvatarForm(request.POST, request.FILES)

        if form.is_valid():
            avatar_file = form.cleaned_data['avatar']

            # Delete old avatar file if exists
            if request.user.avatar:
                request.user.avatar.delete(save=False)

            # Assign new avatar and save
            request.user.avatar = avatar_file
            request.user.save(update_fields=['avatar'])

            avatar_url = request.user.get_avatar_url()

            return JsonResponse({
                'success': True,
                'message': str(_("Avatar uploaded successfully.")),
                'avatar_url': avatar_url,
            })
        else:
            errors = form.errors.get('avatar', [str(_("Invalid file."))])
            return JsonResponse({
                'success': False,
                'error': errors[0] if errors else str(_("Invalid file.")),
            }, status=400)


class ProfileAvatarDeleteView(LoginRequiredMixin, View):
    """Handle avatar deletion via AJAX."""

    def post(self, request):
        if request.user.avatar:
            # Delete the avatar file and clear the field
            request.user.avatar.delete(save=False)
            request.user.avatar = None
            request.user.save(update_fields=['avatar'])

            return JsonResponse({
                'success': True,
                'message': str(_("Avatar deleted successfully.")),
            })
        else:
            return JsonResponse({
                'success': False,
                'error': str(_("No avatar to delete.")),
            }, status=400)

