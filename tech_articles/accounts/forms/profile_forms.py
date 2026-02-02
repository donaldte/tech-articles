"""
Profile forms for user self-management.
Forms for editing profile, uploading avatar, and changing password.
"""
import logging

from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate

from tech_articles.accounts.models import User
from tech_articles.utils.enums import LanguageChoices

logger = logging.getLogger(__name__)


class ProfileEditForm(forms.ModelForm):
    """Form for users to edit their own profile."""

    class Meta:
        model = User
        fields = ['name', 'email', 'preferred_language', 'timezone']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'dashboard-input',
                'placeholder': _('Your full name'),
                'autocomplete': 'name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'dashboard-input',
                'placeholder': _('your@email.com'),
                'autocomplete': 'email',
            }),
            'preferred_language': forms.Select(attrs={
                'class': 'dashboard-input',
            }),
            'timezone': forms.TextInput(attrs={
                'class': 'dashboard-input',
                'placeholder': 'America/Montreal',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = False

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if not email:
            raise forms.ValidationError(_('Email is required.'))

        # Check for duplicates excluding current user
        qs = User.objects.filter(email__iexact=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(_('A user with this email already exists.'))

        return email


class ProfileAvatarForm(forms.Form):
    """Form for uploading/changing user avatar."""

    avatar = forms.ImageField(
        label=_('Avatar'),
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'hidden',
            'accept': 'image/*',
            'id': 'avatar-input',
        }),
    )

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            # Validate file size (max 5MB)
            max_size = 5 * 1024 * 1024
            if avatar.size > max_size:
                raise forms.ValidationError(_('Image file size must be less than 5MB.'))

            # Validate file type
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if avatar.content_type not in allowed_types:
                raise forms.ValidationError(_('Only JPEG, PNG, GIF, and WebP images are allowed.'))

        return avatar


class ProfilePasswordChangeForm(forms.Form):
    """Form for users to change their own password."""

    current_password = forms.CharField(
        label=_('Current password'),
        widget=forms.PasswordInput(attrs={
            'class': 'dashboard-input',
            'placeholder': _('Enter current password'),
            'autocomplete': 'current-password',
        }),
    )
    new_password1 = forms.CharField(
        label=_('New password'),
        widget=forms.PasswordInput(attrs={
            'class': 'dashboard-input',
            'placeholder': _('Enter new password'),
            'autocomplete': 'new-password',
        }),
    )
    new_password2 = forms.CharField(
        label=_('Confirm new password'),
        widget=forms.PasswordInput(attrs={
            'class': 'dashboard-input',
            'placeholder': _('Confirm new password'),
            'autocomplete': 'new-password',
        }),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise forms.ValidationError(_('Current password is incorrect.'))
        return current_password

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('new_password1')
        p2 = cleaned.get('new_password2')

        if p1 and p2 and p1 != p2:
            raise forms.ValidationError(_('New passwords do not match.'))

        if p1:
            try:
                validate_password(p1, user=self.user)
            except forms.ValidationError as e:
                self.add_error('new_password1', e)

        return cleaned

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data['new_password1'])
        if commit:
            self.user.save(update_fields=['password'])
        return self.user
