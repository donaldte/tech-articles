from django.urls import path

from .views import SignupInitView, SignupOTPVerifyView

app_name = "accounts"
urlpatterns = [
    path("signup/", view=SignupInitView.as_view(), name="account_signup"),
    path("signup/verify/", view=SignupOTPVerifyView.as_view(), name="account_signup_verify"),
]
