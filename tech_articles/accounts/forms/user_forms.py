"""
Admin user management forms.
Forms for creating, updating, and changing passwords for users by admin.
"""
from django import forms
from django.contrib.auth import forms as admin_forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password

from tech_articles.accounts.models import User
from tech_articles.utils.enums import UserRole, LanguageChoices



class UserAdminChangeForm(admin_forms.UserChangeForm):
    class Meta(admin_forms.UserChangeForm.Meta):  # type: ignore[name-defined]
        model = User
        field_classes = {"email": forms.EmailField}


class UserAdminCreationForm(admin_forms.AdminUserCreationForm):
    """
    Form for User Creation in the Admin Area.
    To change user signup, see UserSignupForm and UserSocialSignupForm.
    """

    class Meta(admin_forms.UserCreationForm.Meta):  # type: ignore[name-defined]
        model = User
        fields = ("email",)
        field_classes = {"email": forms.EmailField}
        error_messages = {
            "email": {"unique": _("This email has already been taken.")},
        }



class AdminUserCreateForm(forms.ModelForm):
    """Form for admin to create a new user."""

    password1 = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(attrs={
            'class': 'dashboard-input',
            'placeholder': _('Enter password'),
            'autocomplete': 'new-password',
        }),
    )
    password2 = forms.CharField(
        label=_('Confirm password'),
        widget=forms.PasswordInput(attrs={
            'class': 'dashboard-input',
            'placeholder': _('Confirm password'),
            'autocomplete': 'new-password',
        }),
    )

    class Meta:
        model = User
        fields = ['email', 'name', 'role', 'preferred_language', 'timezone', 'is_active']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'dashboard-input',
                'placeholder': _('user@example.com'),
                'autocomplete': 'email',
            }),
            'name': forms.TextInput(attrs={
                'class': 'dashboard-input',
                'placeholder': _('Full name'),
                'autocomplete': 'name',
            }),
            'role': forms.Select(attrs={
                'class': 'dashboard-input',
            }),
            'preferred_language': forms.Select(attrs={
                'class': 'dashboard-input',
            }),
            'timezone': forms.TextInput(attrs={
                'class': 'dashboard-input',
                'placeholder': 'America/Montreal',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'dashboard-checkbox',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = False
        self.fields['is_active'].initial = True

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if not email:
            raise forms.ValidationError(_('Email is required.'))
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(_('A user with this email already exists.'))
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')

        if p1 and p2 and p1 != p2:
            raise forms.ValidationError(_('Passwords do not match.'))

        if p1:
            try:
                validate_password(p1)
            except forms.ValidationError as e:
                self.add_error('password1', e)

        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class AdminUserUpdateForm(forms.ModelForm):
    """Form for admin to update a user's information."""

    class Meta:
        model = User
        fields = ['email', 'name', 'role', 'preferred_language', 'timezone', 'is_active', 'is_staff', 'is_superuser']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'dashboard-input',
                'placeholder': _('user@example.com'),
                'autocomplete': 'email',
            }),
            'name': forms.TextInput(attrs={
                'class': 'dashboard-input',
                'placeholder': _('Full name'),
                'autocomplete': 'name',
            }),
            'role': forms.Select(attrs={
                'class': 'dashboard-input',
            }),
            'preferred_language': forms.Select(attrs={
                'class': 'dashboard-input',
            }),
            'timezone': forms.TextInput(attrs={
                'class': 'dashboard-input',
                'placeholder': 'America/Montreal',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'dashboard-checkbox',
            }),
            'is_staff': forms.CheckboxInput(attrs={
                'class': 'dashboard-checkbox',
            }),
            'is_superuser': forms.CheckboxInput(attrs={
                'class': 'dashboard-checkbox',
            }),
        }

    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)
        self.fields['name'].required = False

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if not email:
            raise forms.ValidationError(_('Email is required.'))

        # Check for duplicates excluding current instance
        qs = User.objects.filter(email__iexact=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(_('A user with this email already exists.'))

        return email

    def clean(self):
        cleaned = super().clean()

        # Prevent user from removing their own superuser/staff status
        if self.current_user and self.instance.pk == self.current_user.pk:
            if self.current_user.is_superuser and not cleaned.get('is_superuser'):
                raise forms.ValidationError(_('You cannot remove your own superuser status.'))
            if self.current_user.is_staff and not cleaned.get('is_staff'):
                raise forms.ValidationError(_('You cannot remove your own staff status.'))
            if self.current_user.is_active and not cleaned.get('is_active'):
                raise forms.ValidationError(_('You cannot deactivate your own account.'))

        return cleaned


class AdminUserPasswordChangeForm(forms.Form):
    """Form for admin to change a user's password."""

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

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('new_password1')
        p2 = cleaned.get('new_password2')

        if p1 and p2 and p1 != p2:
            raise forms.ValidationError(_('Passwords do not match.'))

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
