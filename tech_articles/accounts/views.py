# --- Signup flow views (OTP based) ---
from allauth.account.utils import perform_login
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.conf import settings

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


# --- Login flow views (OTP based) ---

class LoginInitView(View):
    template_name = 'account/login.html'

    def get(self, request):
        from .forms import LoginForm
        form = LoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        from django.contrib.auth import authenticate
        from .forms import LoginForm
        form = LoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email'].lower().strip()
            password = form.cleaned_data['password']

            # Authenticate user with email and password
            user = authenticate(request, email=email, password=password)

            if user is None:
                form.add_error(None, _('Invalid email or password.'))
                return render(request, self.template_name, {'form': form})

            # Check if account is active
            if user.is_active:
                # Login directly
                perform_login(request, user, email_verification='optional')
                return redirect('common:home')
            else:
                # Account is inactive - send OTP for verification
                try:
                    ip_address = SignupInitView._get_client_ip(request)
                    user_agent = request.META.get('HTTP_USER_AGENT', '')
                    create_otp(
                        email=email,
                        purpose='signup_verification',
                        user=user,
                        ip_address=ip_address,
                        user_agent=user_agent,
                    )
                    # Redirect to OTP verification page
                    return redirect("%s?email=%s" % (reverse("accounts:account_login_verify"), email))
                except Exception:
                    form.add_error(None, _('Error sending verification code. Please try again.'))
                    return render(request, self.template_name, {'form': form})


        return render(request, self.template_name, {'form': form})


class LoginOTPVerifyView(View):
    """
    Verify OTP for inactive accounts that tried to login.
    This completes the signup verification process.
    """
    template_name = 'account/login_otp_verify.html'

    def get(self, request):
        email = request.GET.get('email', '')
        from .forms import LoginOTPForm
        form = LoginOTPForm()
        return render(request, self.template_name, {'form': form, 'email': email})

    def post(self, request):
        from .forms import LoginOTPForm
        email = request.POST.get('email', '').lower().strip()
        form = LoginOTPForm(request.POST)

        if form.is_valid():
            code = form.cleaned_data['code']

            try:
                # Verify OTP for signup verification (account activation)
                otp = verify_otp(email, code, 'signup_verification')
                user = otp.user

                if user:
                    # Activate the user
                    user.is_active = True
                    user.save(update_fields=['is_active'])

                    # Login the user
                    perform_login(request, user, email_verification='optional')
                    return redirect('common:home')
                else:
                    form.add_error(None, _('User not found.'))
            except OTPError as e:
                form.add_error('code', str(e))

        return render(request, self.template_name, {'form': form, 'email': email})


# --- Password reset flow views (OTP based) ---

class PasswordResetInitView(View):
    template_name = 'account/password_reset.html'

    def get(self, request):
        from .forms import PasswordResetForm
        form = PasswordResetForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        from .forms import PasswordResetForm
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].lower().strip()

            try:
                ip_address = SignupInitView._get_client_ip(request)
                user_agent = request.META.get('HTTP_USER_AGENT', '')
                create_otp(
                    email=email,
                    purpose='password_reset_verification',
                    user=None,
                    ip_address=ip_address,
                    user_agent=user_agent,
                )
            except Exception:
                form.add_error(None, _('Error sending reset code. Please try again.'))
                return render(request, self.template_name, {'form': form})

            return redirect("%s?email=%s" % (reverse("accounts:account_reset_password_verify"), email))

        return render(request, self.template_name, {'form': form})


class PasswordResetOTPVerifyView(View):
    template_name = 'account/password_reset_otp_verify.html'

    def get(self, request):
        email = request.GET.get('email', '')
        from .forms import PasswordResetOTPForm
        form = PasswordResetOTPForm()
        return render(request, self.template_name, {'form': form, 'email': email})

    def post(self, request):
        from .forms import PasswordResetOTPForm
        email = request.POST.get('email', '').lower().strip()
        form = PasswordResetOTPForm(request.POST)

        if form.is_valid():
            code = form.cleaned_data['code']

            try:
                verify_otp(email, code, 'password_reset_verification')
                user = User.objects.get(email__iexact=email)
                request.session['_password_reset_user_id'] = str(user.id)
                request.session.set_expiry(getattr(settings, 'PASSWORD_RESET_SESSION_TTL', 600))

                return redirect('accounts:account_reset_password_confirm')
            except User.DoesNotExist:
                form.add_error(None, _('User not found.'))
            except OTPError as e:
                form.add_error('code', str(e))

        return render(request, self.template_name, {'form': form, 'email': email})


class PasswordResetConfirmView(View):
    template_name = 'account/password_reset_confirm.html'

    def get(self, request):
        user_id = request.session.get('_password_reset_user_id')
        if not user_id:
            return redirect('accounts:account_reset_password')

        from .forms import PasswordResetConfirmForm
        form = PasswordResetConfirmForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        from .forms import PasswordResetConfirmForm
        user_id = request.session.pop('_password_reset_user_id', None)

        if not user_id:
            return redirect('accounts:account_reset_password')

        form = PasswordResetConfirmForm(request.POST)

        if form.is_valid():
            try:
                user = User.objects.get(id=user_id)
                user.set_password(form.cleaned_data['new_password1'])
                user.save(update_fields=['password'])

                perform_login(request, user, email_verification='optional')
                return redirect('common:home')
            except User.DoesNotExist:
                return redirect('accounts:account_reset_password')

        return render(request, self.template_name, {'form': form})


class LogoutView(View):
    def post(self, request):
        from django.contrib.auth import logout
        logout(request)
        return redirect('common:home')
