"""
Authentication forms for OTP-based signup, login, and password reset flows.
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password

from tech_articles.accounts.models import User


class SignupInitForm(forms.Form):
    """Form for initial signup with email and password."""
    email = forms.EmailField(
        label=_('Email address'),
        widget=forms.EmailInput(attrs={
            'autocomplete': 'email',
            'class': 'form-control',
            'placeholder': 'you@example.com',
        }),
    )
    password1 = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}),
    )
    password2 = forms.CharField(
        label=_('Confirm password'),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}),
    )
    name = forms.CharField(
        label=_('Full name'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(_('This email is already registered.'))
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError(_('Passwords do not match.'))
        # Validate password strength
        try:
            validate_password(p1)
        except forms.ValidationError as e:
            self.add_error('password1', e)
        return cleaned


class SignupOTPForm(forms.Form):
    """Form for OTP verification during signup."""
    code = forms.CharField(
        label=_('Verification code'),
        max_length=10,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000000'}),
    )

    def clean_code(self):
        code = self.cleaned_data.get('code', '').strip()
        if not code.isdigit() or len(code) != 6:
            raise forms.ValidationError(_('Code must be 6 digits.'))
        return code


class LoginForm(forms.Form):
    """Form for email/password login."""
    email = forms.EmailField(
        label=_('Email address'),
        widget=forms.EmailInput(attrs={
            'autocomplete': 'email',
            'class': 'form-control',
            'placeholder': 'you@example.com',
        }),
    )
    password = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'class': 'form-control'}),
    )


class LoginOTPForm(forms.Form):
    """Form for verifying inactive accounts during login."""
    code = forms.CharField(
        label=_('Verification code'),
        max_length=10,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000000'}),
    )

    def clean_code(self):
        code = self.cleaned_data.get('code', '').strip()
        if not code.isdigit() or len(code) != 6:
            raise forms.ValidationError(_('Code must be 6 digits.'))
        return code


class PasswordResetForm(forms.Form):
    """Form for initiating password reset."""
    email = forms.EmailField(
        label=_('Email address'),
        widget=forms.EmailInput(attrs={
            'autocomplete': 'email',
            'class': 'form-control',
            'placeholder': 'you@example.com',
        }),
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and not User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(_('No account found with this email address.'))
        return email


class PasswordResetOTPForm(forms.Form):
    """Form for OTP verification during password reset."""
    code = forms.CharField(
        label=_('Verification code'),
        max_length=10,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000000'}),
    )

    def clean_code(self):
        code = self.cleaned_data.get('code', '').strip()
        if not code.isdigit() or len(code) != 6:
            raise forms.ValidationError(_('Code must be 6 digits.'))
        return code


class PasswordResetConfirmForm(forms.Form):
    """Form for setting a new password after OTP verification."""
    new_password1 = forms.CharField(
        label=_('New password'),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}),
    )
    new_password2 = forms.CharField(
        label=_('Confirm new password'),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}),
    )

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('new_password1')
        p2 = cleaned.get('new_password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError(_('Passwords do not match.'))
        # Validate password strength
        try:
            validate_password(p1)
        except forms.ValidationError as e:
            self.add_error('new_password1', e)
        return cleaned
