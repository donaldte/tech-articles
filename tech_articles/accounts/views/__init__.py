"""
Account views module for Runbookly.
Contains views for authentication, user management, and profile.
"""
from .auth_views import (
    SignupInitView,
    SignupOTPVerifyView,
    LoginInitView,
    LoginOTPVerifyView,
    PasswordResetInitView,
    PasswordResetOTPVerifyView,
    PasswordResetConfirmView,
    LogoutView,
    ResendOTPView,
)
from .user_views import (
    UserListView,
    UserCreateView,
    UserDetailView,
    UserUpdateView,
    UserDeleteView,
    UserPasswordChangeView,
)
from .profile_views import (
    ProfileEditView,
    ProfileSecurityView,
    ProfileAvatarUploadView,
    ProfileAvatarDeleteView,
)

__all__ = [
    # Auth views
    "SignupInitView",
    "SignupOTPVerifyView",
    "LoginInitView",
    "LoginOTPVerifyView",
    "PasswordResetInitView",
    "PasswordResetOTPVerifyView",
    "PasswordResetConfirmView",
    "LogoutView",
    "ResendOTPView",
    # Admin user management views
    "UserListView",
    "UserCreateView",
    "UserDetailView",
    "UserUpdateView",
    "UserDeleteView",
    "UserPasswordChangeView",
    # Profile views
    "ProfileEditView",
    "ProfileSecurityView",
    "ProfileAvatarUploadView",
    "ProfileAvatarDeleteView",
]
