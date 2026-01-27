# Plan: Custom Authentication (OTP + Providers) with Model + Cache Hybrid

## Recommended approach: Model + Cache

Rationale:
- Model (OTPVerification): full audit trail, persistence, GDPR compliance.
- Cache: fast rate-limiting, counters, performance.
- Hybrid: DB for persistence/verification + cache for request throttling.

All user-facing strings must be internationalized:
- In Python code use gettext_lazy as _ or gettext where appropriate.
- In templates use {% load i18n %} and {% trans %}/{% blocktrans %}.
- Email subjects and bodies should be localized (activate language before rendering).

---

TL;DR

Implement a complete OTP-based authentication flow backing OTPs with a Django model OTPVerification (audit) and cache-based rate-limiting for performance. Separate purposes for signup, login, and password reset. Reuse allauth utilities (perform_login, adapters) but use custom views/URLs (do not include allauth.urls globally). Provide tests.

---

Step-by-step implementation overview

1) Create OTPVerification model
- File: tech_articles/accounts/models.py
- Purpose: store hashed OTP, purpose (signup/login/password_reset), attempts, expiry, request metadata (IP, user-agent), and verification state.
- Use gettext_lazy for verbose_name/help_text.
- Add indexes on (email, purpose, is_verified, expires_at) and created_at.
- Provide helper methods: is_expired, is_valid_code, can_attempt, increment_attempts, mark_verified, get_valid.
- Run: python manage.py makemigrations && python manage.py migrate

2) Add OTP settings
- File: config/settings/base.py
- Add OTP configuration constants and make them translatable where displayed (settings themselves are not translated).
- Example keys: OTP_CODE_LENGTH, OTP_TTL_SECONDS, OTP_MAX_ATTEMPTS, OTP_RATE_LIMIT_WINDOW, OTP_RATE_LIMIT_MAX_REQUESTS, OTP_HASH_ALGORITHM, PASSWORD_RESET_SESSION_TTL

3) Create otp utilities
- File: tech_articles/accounts/otp_utils.py (new)
- Responsibilities:
  - generate numeric OTP (secrets), hash with Django make_password, verify with check_password
  - rate-limit via Django cache (per-email keys)
  - create_otp: validate email, enforce rate limit, create OTPVerification record, enqueue send_otp_email Celery task
  - verify_otp: fetch latest valid OTPVerification.get_valid, check expiration, attempts, validate code, mark verified
  - resend_otp helper
- Exceptions should be specific classes (OTPRateLimitExceeded, OTPNotFound, OTPExpired, OTPMaxAttemptsExceeded, OTPInvalidCode) and messages must use gettext_lazy when raised.
- Ensure logs are localized only for operator readability; exceptions shown to users must be translated.

4) Create forms
- File: tech_articles/accounts/forms.py
- Use django's forms and allauth SignupForm extension where useful.
- All labels/help_text/validation messages must use gettext_lazy.
- Validate email existence (for login/reset) and email uniqueness (for signup).
- OTP code fields validate numeric length (use settings.OTP_CODE_LENGTH).

5) Implement views
- File: tech_articles/accounts/views.py
- Implement class-based views for:
  - SignupInitView: create inactive user, create_otp(purpose='signup_verification'), redirect to OTP verify page
  - SignupOTPVerifyView: verify_otp, activate user, perform_login
  - LoginInitView / LoginOTPVerifyView: send OTP for existing users, verify and login
  - PasswordResetInitView / PasswordResetOTPVerifyView / PasswordResetConfirmView: send OTP, verify, store user id in session with TTL, allow password reset and optional auto-login
  - LogoutView: logout and redirect
- Use perform_login(request, user, email_verification='optional') from allauth.account.utils
- Use gettext_lazy for all user messages. All redirects/URLs should use named URLs (reverse) and preserve i18n patterns.

6) Templates
- Directory: tech_articles/templates/account/
- Create templates listed in the original plan.
- All templates must load i18n ({% load i18n %}) and wrap visible strings with {% trans %} or {% blocktrans %}.
- Include CSRF tokens in forms, and display form.non_field_errors / form.field errors.

7) Email templates
- Directory: tech_articles/templates/account/email/
- Provide subject lines and bodies for each purpose:
  - otp_signup_verification_message.txt / .html
  - otp_login_verification_message.txt / .html
  - otp_password_reset_verification_message.txt / .html
- Use template translation tags and context variables (code, otp_ttl_minutes, site_name).
- Before rendering, activate the user's preferred language or use the request's language.

8) Celery tasks
- File: tech_articles/accounts/tasks.py
- send_otp_email task should:
  - Accept email, purpose, code, otp_id
  - Map purpose to templates and localized subjects (use gettext_lazy or translate subject strings)
  - Render html and text templates, send via send_mail with html_message
  - Retry on failure with exponential backoff
  - Log actions (logger), avoid leaking codes in logs in production (mask if needed)

9) URLs
- File: tech_articles/accounts/urls.py
- Provide explicit paths with app_name='accounts' and named routes for all views.
- Keep socialaccount urls separately if needed (e.g., include allauth.socialaccount.urls at 'accounts/social/').

10) Project URLs
- File: config/urls.py
- Replace include('allauth.urls') with include('tech_articles.accounts.urls', namespace='accounts')
- Optionally keep social callbacks from allauth under 'accounts/social/' if OAuth flows are desired.
- Use i18n_patterns for internationalized routes.

11) Settings: allauth integration
- File: config/settings/base.py
- Keep ACCOUNT_AUTHENTICATION_METHOD='email', ACCOUNT_EMAIL_VERIFICATION='none' (OTP handles it)
- Set ACCOUNT_ADAPTER and SOCIALACCOUNT_ADAPTER to your custom adapters if implementing social logic
- Set LOGIN_URL and LOGIN_REDIRECT_URL to named routes.

12) Optional: social adapters
- File: tech_articles/accounts/adapters.py
- In SocialAccountAdapter.pre_social_login, try to link social login to existing user by email; if provider returns no email, store sociallogin in session and redirect to email capture flow.
- All user-visible messages must be internationalized.

13) Tests
- Directory: tech_articles/accounts/tests/
- Create unit tests for:
  - test_otp_utils.py (generation, hashing, verification, rate-limiting)
  - test_signup_otp.py (signup init, OTP flow, activation)
  - test_login_otp.py (login init and OTP verification)
  - test_password_reset_otp.py (reset flow and session TTL)
  - test_social.py (adapter linking behavior)
- Use Django's translation.activate to test localization where applicable.

Security & edge cases (implement these in code)
- Rate-limiting: protect create_otp by cache counters per email (and possibly per IP).
- Attempts limiting: use OTPVerification.attempts_count and block after max_attempts.
- Expiration: always check expires_at when verifying.
- Inactive-user-on-login: redirect to signup verify flow or show appropriate localized message.
- Session TTL for password reset: short expiry (settings.PASSWORD_RESET_SESSION_TTL).
- CSRF: all forms include {% csrf_token %}.
- Email content: avoid including unnecessary identifying data; localize content and subject.
- Admin: consider admin registration for OTPVerification model for auditing.

Migration checklist
- Create and apply migration for OTPVerification model.
- Run tests locally and check email rendering.
- Deploy migration to staging, test end-to-end email delivery and rate-limits.
- Monitor logs and set feature flag / gradual rollout if required.

Further considerations (extensions)
- Passwordless flow (OTP only): mark in settings feature flag.
- SMS/other channels: add channel field to OTPVerification and pluggable senders.
- Resend endpoint and backoff UI feedback.
- Internationalized email templates per language.
- Admin interface and retention policy for OTP records (GDPR).

Quick commands
- makemigrations: python manage.py makemigrations tech_articles.accounts
- migrate: python manage.py migrate
- run tests: pytest or python manage.py test
- collect static / restart celery + workers after task changes.

Status: plan translated to English and updated to explicitly require i18n for all user-facing text. Proceed to implement files referenced above, following the file list and i18n guidance.
