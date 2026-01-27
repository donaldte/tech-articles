# --- Signup flow views (OTP based) ---
from allauth.account.utils import perform_login
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View

from tech_articles.accounts.models import User
from .forms import SignupInitForm, SignupOTPForm
from .otp_utils import create_otp, verify_otp, OTPError


class SignupInitView(View):
    template_name = 'tech-articles/home/pages/accounts/signup.html'

    def get(self, request):
        form = SignupInitForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = SignupInitForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].lower().strip()
            password = form.cleaned_data['password1']
            name = form.cleaned_data.get('name', '')

            # Create inactive user
            user = User.objects.create_user(
                email=email,
                password=password,
                name=name,
                is_active=False,
            )

            # Create and send OTP
            try:
                ip_address = self._get_client_ip(request)
                user_agent = request.META.get('HTTP_USER_AGENT', '')
                create_otp(
                    email=email,
                    purpose='signup_verification',
                    user=user,
                    ip_address=ip_address,
                    user_agent=user_agent,
                )
            except Exception:
                # Log error, delete user, show error
                user.delete()
                form.add_error(None, _('Error sending verification code. Please try again.'))
                return render(request, self.template_name, {'form': form})

            return redirect("%s?email=%s" % (reverse("accounts:account_signup_verify"), email))

        return render(request, self.template_name, {'form': form})

    @staticmethod
    def _get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')


class SignupOTPVerifyView(View):
    template_name = 'tech-articles/home/pages/accounts/signup_otp_verify.html'

    def get(self, request):
        email = request.GET.get('email', '')
        form = SignupOTPForm()
        return render(request, self.template_name, {'form': form, 'email': email})

    def post(self, request):
        email = request.POST.get('email', '').lower().strip()
        form = SignupOTPForm(request.POST)

        if form.is_valid():
            code = form.cleaned_data['code']

            try:
                otp = verify_otp(email, code, 'signup_verification')

                # Activate user
                user = otp.user
                if user:
                    user.is_active = True
                    user.save(update_fields=['is_active'])

                    # Perform login
                    perform_login(request, user, email_verification='optional')

                    return redirect('common:home')  # or home
            except OTPError as e:
                form.add_error('code', str(e))

        return render(request, self.template_name, {'form': form, 'email': email})
