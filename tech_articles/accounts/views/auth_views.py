"""
Authentication views for OTP-based signup, login, and password reset flows.
"""
from allauth.account.utils import perform_login
from django.core.signing import TimestampSigner
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.conf import settings

from tech_articles.accounts.models import User
from tech_articles.accounts.forms import (
    SignupInitForm, SignupOTPForm,
    LoginForm, LoginOTPForm,
    PasswordResetForm, PasswordResetOTPForm, PasswordResetConfirmForm,
)
from tech_articles.accounts.otp_utils import (
    create_otp, verify_otp, OTPError,
    create_otp_session, validate_otp_session, clear_otp_session,
    OTPSessionError, OTPSessionExpired,
)


def get_client_ip(request):
    """Extract client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


class SignupInitView(View):
    """Initial signup view with email and password."""
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
                ip_address = get_client_ip(request)
                user_agent = request.META.get('HTTP_USER_AGENT', '')
                otp = create_otp(
                    email=email,
                    purpose='signup_verification',
                    user=user,
                    ip_address=ip_address,
                    user_agent=user_agent,
                )

                # Create secure session token (stores email & otp_id server-side)
                create_otp_session(
                    request=request,
                    email=email,
                    purpose='signup_verification',
                    otp_id=str(otp.id),
                )

                # Mark that OTP was just sent to initialize timer on verification page
                request.session['otp_just_sent'] = True

            except Exception:
                user.delete()
                form.add_error(None, _('Error sending verification code. Please try again.'))
                return render(request, self.template_name, {'form': form})

            return redirect(reverse("accounts:account_signup_verify"))

        return render(request, self.template_name, {'form': form})


class SignupOTPVerifyView(View):
    """Verify OTP for signup completion."""
    template_name = 'tech-articles/home/pages/accounts/signup_otp_verify.html'
    purpose = 'signup_verification'

    def get(self, request):
        try:
            session_data = validate_otp_session(request, self.purpose)
            email = session_data.get('email', '')
        except OTPSessionError:
            return redirect(reverse("accounts:account_signup"))

        form = SignupOTPForm()
        masked_email = self.mask_email(email)
        otp_just_sent = request.session.pop('otp_just_sent', False)

        return render(request, self.template_name, {
            'form': form,
            'masked_email': masked_email,
            'otp_just_sent': otp_just_sent,
        })

    def post(self, request):
        form = SignupOTPForm(request.POST)

        try:
            session_data = validate_otp_session(request, self.purpose)
            email = session_data.get('email', '')
        except OTPSessionExpired:
            form.add_error(None, _('Verification session expired. Please sign up again.'))
            return render(request, self.template_name, {'form': form, 'masked_email': ''})
        except OTPSessionError:
            return redirect(reverse("accounts:account_signup"))

        if form.is_valid():
            code = form.cleaned_data['code']

            try:
                otp = verify_otp(email, code, self.purpose)

                user = otp.user
                if user:
                    user.is_active = True
                    user.save(update_fields=['is_active'])
                    clear_otp_session(request, self.purpose)
                    perform_login(request, user, email_verification='optional')
                    return redirect('common:home')
            except OTPError as e:
                form.add_error('code', str(e))

        masked_email = self.mask_email(email) if email else ''
        return render(request, self.template_name, {'form': form, 'masked_email': masked_email})

    @staticmethod
    def mask_email(email: str) -> str:
        """Mask email for display."""
        if not email or '@' not in email:
            return email
        local, domain = email.split('@', 1)
        if len(local) <= 2:
            masked_local = local[0] + '***'
        else:
            masked_local = local[0] + '***' + local[-1]
        return f"{masked_local}@{domain}"


class ResendOTPView(View):
    """Securely resend OTP using the existing session."""

    def post(self, request):
        from django.http import JsonResponse
        from tech_articles.accounts.otp_utils import OTPRateLimitExceeded

        purpose = request.POST.get('purpose', 'signup_verification')

        try:
            session_data = validate_otp_session(request, purpose)
            email = session_data.get('email', '')
        except OTPSessionError:
            return JsonResponse({
                'success': False,
                'error': str(_('No active verification session. Please start again.'))
            }, status=400)

        if not email:
            return JsonResponse({
                'success': False,
                'error': str(_('Invalid session.'))
            }, status=400)

        try:
            user = None
            if purpose in ('signup_verification', 'login_verification'):
                try:
                    user = User.objects.get(email__iexact=email)
                except User.DoesNotExist:
                    pass
            elif purpose == 'password_reset_verification':
                try:
                    user = User.objects.get(email__iexact=email)
                except User.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'error': str(_('User not found.'))
                    }, status=400)

            ip_address = get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')

            otp = create_otp(
                email=email,
                purpose=purpose,
                user=user,
                ip_address=ip_address,
                user_agent=user_agent,
            )

            create_otp_session(
                request=request,
                email=email,
                purpose=purpose,
                otp_id=str(otp.id),
            )

            return JsonResponse({
                'success': True,
                'message': str(_('Verification code sent successfully.'))
            })

        except OTPRateLimitExceeded:
            return JsonResponse({
                'success': False,
                'error': str(_('Too many requests. Please wait before requesting another code.'))
            }, status=429)
        except Exception:
            return JsonResponse({
                'success': False,
                'error': str(_('Error sending verification code. Please try again.'))
            }, status=500)


class LoginInitView(View):
    """Login view with email + password."""
    template_name = 'tech-articles/home/pages/accounts/login.html'

    def get(self, request):
        form = LoginForm()
        next_url = request.GET.get('next')
        if next_url:
            request.session['login_next_url'] = next_url
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email'].lower().strip()
            password = form.cleaned_data['password']

            try:
                user = User.objects.get(email__iexact=email)
            except User.DoesNotExist:
                form.add_error(None, _('Invalid email or password.'))
                return render(request, self.template_name, {'form': form})

            if not user.check_password(password):
                form.add_error(None, _('Invalid email or password.'))
                return render(request, self.template_name, {'form': form})

            if user.is_active:
                from django.contrib.auth import login as auth_login
                auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                next_url = request.session.pop('login_next_url', None)
                return redirect(self.get_safe_redirect_url(request, next_url))
            else:
                try:
                    ip_address = get_client_ip(request)
                    user_agent = request.META.get('HTTP_USER_AGENT', '')
                    otp = create_otp(
                        email=email,
                        purpose='signup_verification',
                        user=user,
                        ip_address=ip_address,
                        user_agent=user_agent,
                    )

                    create_otp_session(
                        request=request,
                        email=email,
                        purpose='signup_verification',
                        otp_id=str(otp.id),
                    )

                    request.session['otp_just_sent'] = True
                    return redirect(reverse("accounts:account_login_verify"))
                except Exception:
                    form.add_error(None, _('Error sending verification code. Please try again.'))
                    return render(request, self.template_name, {'form': form})

        return render(request, self.template_name, {'form': form})

    @staticmethod
    def get_safe_redirect_url(request, next_url=None):
        """Get a safe redirect URL."""
        from django.utils.http import url_has_allowed_host_and_scheme

        if not next_url:
            return 'common:home'

        if url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return next_url

        return 'common:home'


class LoginOTPVerifyView(View):
    """Verify OTP for inactive accounts."""
    template_name = 'tech-articles/home/pages/accounts/login_otp_verify.html'
    purpose = 'signup_verification'

    def get(self, request):
        try:
            session_data = validate_otp_session(request, self.purpose)
            email = session_data.get('email', '')
        except OTPSessionError:
            return redirect(reverse("accounts:account_login"))

        form = LoginOTPForm()
        masked_email = SignupOTPVerifyView.mask_email(email)
        otp_just_sent = request.session.pop('otp_just_sent', False)

        return render(request, self.template_name, {
            'form': form,
            'masked_email': masked_email,
            'otp_just_sent': otp_just_sent,
        })

    def post(self, request):
        form = LoginOTPForm(request.POST)

        try:
            session_data = validate_otp_session(request, self.purpose)
            email = session_data.get('email', '')
        except OTPSessionExpired:
            form.add_error(None, _('Verification session expired. Please login again.'))
            return render(request, self.template_name, {'form': form, 'masked_email': ''})
        except OTPSessionError:
            return redirect(reverse("accounts:account_login"))

        if form.is_valid():
            code = form.cleaned_data['code']

            try:
                otp = verify_otp(email, code, self.purpose)
                user = otp.user

                if user:
                    user.is_active = True
                    user.save(update_fields=['is_active'])
                    clear_otp_session(request, self.purpose)
                    perform_login(request, user, email_verification='optional')
                    next_url = request.session.pop('login_next_url', None)
                    return redirect(LoginInitView.get_safe_redirect_url(request, next_url))
                else:
                    form.add_error(None, _('User not found.'))
            except OTPError as e:
                form.add_error('code', str(e))

        masked_email = SignupOTPVerifyView.mask_email(email) if email else ''
        return render(request, self.template_name, {'form': form, 'masked_email': masked_email})


class PasswordResetInitView(View):
    """Initiate password reset by sending OTP."""
    template_name = 'tech-articles/home/pages/accounts/password_reset.html'
    purpose = 'password_reset_verification'

    def get(self, request):
        form = PasswordResetForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].lower().strip()

            try:
                user = User.objects.get(email__iexact=email)
            except User.DoesNotExist:
                return redirect(reverse("accounts:account_reset_password_verify"))

            try:
                ip_address = get_client_ip(request)
                user_agent = request.META.get('HTTP_USER_AGENT', '')
                otp = create_otp(
                    email=email,
                    purpose=self.purpose,
                    user=user,
                    ip_address=ip_address,
                    user_agent=user_agent,
                )

                create_otp_session(
                    request=request,
                    email=email,
                    purpose=self.purpose,
                    otp_id=str(otp.id),
                )

                request.session['otp_just_sent'] = True

            except Exception:
                form.add_error(None, _('Error sending reset code. Please try again.'))
                return render(request, self.template_name, {'form': form})

            return redirect(reverse("accounts:account_reset_password_verify"))

        return render(request, self.template_name, {'form': form})


class PasswordResetOTPVerifyView(View):
    """Verify OTP for password reset."""
    template_name = 'tech-articles/home/pages/accounts/password_reset_otp_verify.html'
    purpose = 'password_reset_verification'

    def get(self, request):
        try:
            session_data = validate_otp_session(request, self.purpose)
            email = session_data.get('email', '')
        except OTPSessionError:
            return redirect(reverse("accounts:account_reset_password"))

        form = PasswordResetOTPForm()
        masked_email = SignupOTPVerifyView.mask_email(email)
        otp_just_sent = request.session.pop('otp_just_sent', False)

        return render(request, self.template_name, {
            'form': form,
            'masked_email': masked_email,
            'otp_just_sent': otp_just_sent,
        })

    def post(self, request):
        form = PasswordResetOTPForm(request.POST)

        try:
            session_data = validate_otp_session(request, self.purpose)
            email = session_data.get('email', '')
        except OTPSessionExpired:
            form.add_error(None, _('Verification session expired. Please try again.'))
            return render(request, self.template_name, {'form': form, 'masked_email': ''})
        except OTPSessionError:
            return redirect(reverse("accounts:account_reset_password"))

        if form.is_valid():
            code = form.cleaned_data['code']

            try:
                otp = verify_otp(email, code, self.purpose)
                user = otp.user

                if user:
                    clear_otp_session(request, self.purpose)

                    signer = TimestampSigner(salt='password-reset-confirm')
                    signed_user_id = signer.sign(str(user.id))
                    request.session['_password_reset_token'] = signed_user_id
                    request.session.set_expiry(getattr(settings, 'PASSWORD_RESET_SESSION_TTL', 600))

                    return redirect('accounts:account_reset_password_confirm')
                else:
                    form.add_error(None, _('User not found.'))
            except OTPError as e:
                form.add_error('code', str(e))

        masked_email = SignupOTPVerifyView.mask_email(email) if email else ''
        return render(request, self.template_name, {'form': form, 'masked_email': masked_email})


class PasswordResetConfirmView(View):
    """Confirm new password after OTP verification."""
    template_name = 'tech-articles/home/pages/accounts/password_reset_confirm.html'
    purpose = 'password_reset_verification'

    def get(self, request):
        user = self._get_validated_user(request)
        if not user:
            return redirect('accounts:account_reset_password')

        form = PasswordResetConfirmForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        user = self._get_validated_user(request, consume=False)
        if not user:
            return redirect('accounts:account_reset_password')

        form = PasswordResetConfirmForm(request.POST)

        if form.is_valid():
            user.set_password(form.cleaned_data['new_password1'])
            user.save(update_fields=['password'])

            clear_otp_session(request, self.purpose)

            from django.contrib import messages
            messages.success(request, _('Your password has been changed. Please sign in with your new password.'))
            return redirect('accounts:account_login')

        return render(request, self.template_name, {'form': form})

    def _get_validated_user(self, request, consume: bool = False) -> User | None:
        """Validate the password reset token and return the user."""
        from django.core.signing import TimestampSigner, BadSignature, SignatureExpired

        if consume:
            signed_token = request.session.pop('_password_reset_token', None)
        else:
            signed_token = request.session.get('_password_reset_token')

        if not signed_token:
            return None

        try:
            signer = TimestampSigner(salt='password-reset-confirm')
            max_age = getattr(settings, 'PASSWORD_RESET_SESSION_TTL', 600)
            user_id = signer.unsign(signed_token, max_age=max_age)
            return User.objects.get(id=user_id)
        except (BadSignature, SignatureExpired, User.DoesNotExist):
            request.session.pop('_password_reset_token', None)
            return None


class LogoutView(View):
    """Logout view."""
    def post(self, request):
        from django.contrib.auth import logout
        logout(request)
        return redirect('common:home')
