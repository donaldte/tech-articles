"""
Authentication URLs for OTP-based signup, login, and password reset flows.
"""
from django.urls import path

from tech_articles.accounts.views import (
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

urlpatterns = [
    # Signup flow
    path("signup/", view=SignupInitView.as_view(), name="account_signup"),
    path("signup/verify/", view=SignupOTPVerifyView.as_view(), name="account_signup_verify"),

    # Login flow
    path("login/", view=LoginInitView.as_view(), name="account_login"),
    path("login/verify/", view=LoginOTPVerifyView.as_view(), name="account_login_verify"),

    # Password reset flow
    path("password/reset/", view=PasswordResetInitView.as_view(), name="account_reset_password"),
    path("password/reset/verify/", view=PasswordResetOTPVerifyView.as_view(), name="account_reset_password_verify"),
    path("password/reset/confirm/", view=PasswordResetConfirmView.as_view(), name="account_reset_password_confirm"),

    # OTP Resend (secure, session-based)
    path("otp/resend/", view=ResendOTPView.as_view(), name="otp_resend"),

    # Logout
    path("logout/", view=LogoutView.as_view(), name="account_logout"),
]
