"""
Profile views for user self-management.
Views for editing profile, security settings, and avatar management.
"""
import logging
import uuid

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect
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


def get_s3_client():
    """
    Get AWS S3 client.
    Returns None if credentials are not configured.
    """
    try:
        import boto3
        from botocore.exceptions import NoCredentialsError, ClientError

        aws_access_key = getattr(settings, 'AWS_ACCESS_KEY_ID', None)
        aws_secret_key = getattr(settings, 'AWS_SECRET_ACCESS_KEY', None)
        aws_region = getattr(settings, 'AWS_S3_REGION_NAME', 'us-east-1')

        if not aws_access_key or not aws_secret_key:
            logger.warning("AWS credentials not configured")
            return None

        return boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region,
        )
    except ImportError:
        logger.warning("boto3 not installed")
        return None
    except Exception as e:
        logger.error(f"Error creating S3 client: {e}")
        return None


def upload_avatar_to_s3(file, user_id: str) -> str | None:
    """
    Upload avatar to S3 bucket.

    Args:
        file: The uploaded file object
        user_id: User's UUID for generating unique key

    Returns:
        S3 key if successful, None otherwise
    """
    s3_client = get_s3_client()
    bucket_name = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', None)

    if not s3_client or not bucket_name:
        logger.warning("S3 not configured, cannot upload avatar")
        return None

    try:
        # Generate unique filename
        file_ext = file.name.split('.')[-1].lower()
        s3_key = f"avatars/{user_id}/{uuid.uuid4().hex}.{file_ext}"

        # Upload to S3
        s3_client.upload_fileobj(
            file,
            bucket_name,
            s3_key,
            ExtraArgs={
                'ContentType': file.content_type,
                'ACL': 'public-read',  # Make avatar publicly accessible
            }
        )

        logger.info(f"Avatar uploaded to S3: {s3_key}")
        return s3_key

    except Exception as e:
        logger.error(f"Error uploading avatar to S3: {e}")
        return None


def delete_avatar_from_s3(s3_key: str) -> bool:
    """
    Delete avatar from S3 bucket.

    Args:
        s3_key: The S3 key/path of the avatar

    Returns:
        True if successful or no key to delete, False on error
    """
    if not s3_key:
        return True

    s3_client = get_s3_client()
    bucket_name = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', None)

    if not s3_client or not bucket_name:
        logger.warning("S3 not configured, cannot delete avatar")
        return False

    try:
        s3_client.delete_object(Bucket=bucket_name, Key=s3_key)
        logger.info(f"Avatar deleted from S3: {s3_key}")
        return True
    except Exception as e:
        logger.error(f"Error deleting avatar from S3: {e}")
        return False


def get_avatar_url(s3_key: str) -> str | None:
    """
    Get the public URL for an avatar.

    Args:
        s3_key: The S3 key/path of the avatar

    Returns:
        Public URL or None
    """
    if not s3_key:
        return None

    bucket_name = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', None)
    region = getattr(settings, 'AWS_S3_REGION_NAME', 'us-east-1')
    custom_domain = getattr(settings, 'AWS_S3_CUSTOM_DOMAIN', None)

    if custom_domain:
        return f"https://{custom_domain}/{s3_key}"

    if bucket_name:
        return f"https://{bucket_name}.s3.{region}.amazonaws.com/{s3_key}"

    return None


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

        # Get avatar URL if exists
        if self.request.user.avatar_key:
            context["avatar_url"] = get_avatar_url(self.request.user.avatar_key)
        else:
            context["avatar_url"] = None

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

            # Delete old avatar if exists
            if request.user.avatar_key:
                delete_avatar_from_s3(request.user.avatar_key)

            # Upload new avatar
            new_key = upload_avatar_to_s3(avatar_file, str(request.user.id))

            if new_key:
                request.user.avatar_key = new_key
                request.user.save(update_fields=['avatar_key'])

                avatar_url = get_avatar_url(new_key)

                return JsonResponse({
                    'success': True,
                    'message': str(_("Avatar uploaded successfully.")),
                    'avatar_url': avatar_url,
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': str(_("Failed to upload avatar. Storage not configured.")),
                }, status=500)
        else:
            errors = form.errors.get('avatar', [str(_("Invalid file."))])
            return JsonResponse({
                'success': False,
                'error': errors[0] if errors else str(_("Invalid file.")),
            }, status=400)


class ProfileAvatarDeleteView(LoginRequiredMixin, View):
    """Handle avatar deletion via AJAX."""

    def post(self, request):
        if request.user.avatar_key:
            # Delete from S3
            deleted = delete_avatar_from_s3(request.user.avatar_key)

            # Clear the key in database regardless
            request.user.avatar_key = ""
            request.user.save(update_fields=['avatar_key'])

            if deleted:
                return JsonResponse({
                    'success': True,
                    'message': str(_("Avatar deleted successfully.")),
                })
            else:
                return JsonResponse({
                    'success': True,
                    'message': str(_("Avatar reference removed.")),
                })
        else:
            return JsonResponse({
                'success': False,
                'error': str(_("No avatar to delete.")),
            }, status=400)
