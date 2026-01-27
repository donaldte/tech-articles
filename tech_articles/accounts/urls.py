from django.urls import path

from .views import (
    SignupInitView, SignupOTPVerifyView,
    LoginInitView, LoginOTPVerifyView,
    PasswordResetInitView, PasswordResetOTPVerifyView, PasswordResetConfirmView,
    LogoutView,
    user_detail_view, user_redirect_view, user_update_view,
)

app_name = "accounts"
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

    # Logout
    path("logout/", view=LogoutView.as_view(), name="account_logout"),

    # User management (existing)
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("~update/", view=user_update_view, name="update"),
    path("<int:pk>/", view=user_detail_view, name="detail"),
]
