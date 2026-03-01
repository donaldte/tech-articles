# tech-articles

Premium technical article platform with paid bookings, newsletters, and AWS integration.

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

License: MIT

This project has been setup using the new version of the cookiecutter-django template wtih uv 

## check uv version
```bash
uv --version
```

## install uv if not installed
follow the instructions here https://docs.astral.sh/uv/getting-started/installation/#standalone-installer


##  synchronize means to install the dependencies
```bash
uv sync
```

## run the server
```bash
uv run python manage.py runserver
```


## Settings

Moved to [settings](https://cookiecutter-django.readthedocs.io/en/latest/1-getting-started/settings.html).

## Basic Commands

### Setting Up Your Users

- To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

- To create a **superuser account**, use this command:

      uv run python manage.py createsuperuser

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

### Type checks

Running type checks with mypy:

    uv run mypy tech_articles

### Test coverage

To run the tests, check your test coverage, and generate an HTML coverage report:

    uv run coverage run -m pytest
    uv run coverage html
    uv run open htmlcov/index.html

#### Running tests with pytest

    uv run pytest

### Live reloading and Sass CSS compilation

Moved to [Live reloading and SASS compilation](https://cookiecutter-django.readthedocs.io/en/latest/2-local-development/developing-locally.html#using-webpack-or-gulp).

## Frontend / Styles (Tailwind CSS)

The project uses Tailwind CSS for styles. To work locally and see style changes in real time, follow these steps:

Prerequisites
- Node.js 20 (or newer)
- npm 9 (or newer)

Install and run (development)
1. Install JavaScript dependencies:

```bash
npm install
```

2. Start the Tailwind watcher (rebuilds styles in real time):

```bash
npm run dev
```

- The Tailwind pipeline reads `tech_articles/static/css/input.css` and writes `tech_articles/static/css/output.css`.
- To build for production:

```bash
npm run build
```

Environment configuration

Before running the project, copy and configure the environment file:

```bash
cp .env-example .env
# then edit .env and fill sensitive values (DJANGO_SECRET_KEY, DB_PASSWORD, etc.)
```

Never commit a `.env` file containing secrets to version control.

### Celery

This app comes with Celery.

To run a celery worker:

```bash
cd tech_articles
uv run celery -A config.celery_app worker -l info
```

Please note: For Celery's import magic to work, it is important _where_ the celery commands are run. If you are in the same folder with _manage.py_, you should be right.

To run [periodic tasks](https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html), you'll need to start the celery beat scheduler service. You can start it as a standalone process:

```bash
cd tech_articles
uv run celery -A config.celery_app beat
```

or you can embed the beat service inside a worker with the `-B` option (not recommended for production use):

```bash
cd tech_articles
uv run celery -A config.celery_app worker -B -l info
```

## Deployment

The following details how to deploy this application.

### Docker

See detailed [cookiecutter-django Docker documentation](https://cookiecutter-django.readthedocs.io/en/latest/3-deployment/deployment-with-docker.html).

### Environment Configuration

Before deploying, copy and configure the environment file:

```bash
cp .env.example .env
# then edit .env and fill in all sensitive values
```

Refer to `.env.example` for the complete list of required variables. Never commit a `.env` file containing secrets.

### Initial Setup (run once after deployment)

After the first deployment, run the following command **once** inside the Django Docker container to load the initial subscription plans:

```bash
docker compose -f docker-compose.production.yml exec django python manage.py load_subscription_plans --clear
```

> ⚠️ **Important:** This command must only be run **once**, right after the initial deployment. Running it multiple times will reset all existing subscription plan data.

## Social Authentication Setup (GitHub, GitLab, Google)

The application supports social login via GitHub, GitLab and Google using `django-allauth`.

### 1. Create OAuth Applications

#### Google

1. Go to [Google Cloud Console](https://console.cloud.google.com/) → **APIs & Services** → **Credentials**.
2. Click **Create Credentials** → **OAuth client ID** → **Web application**.
3. Add `https://<your-domain>/accounts/google/login/callback/` to **Authorized redirect URIs**.
4. Copy the **Client ID** and **Client Secret**.

#### GitHub

1. Go to [GitHub Developer Settings](https://github.com/settings/developers) → **OAuth Apps** → **New OAuth App**.
2. Set **Authorization callback URL** to `https://<your-domain>/accounts/github/login/callback/`.
3. Copy the **Client ID** and generate a **Client Secret**.

#### GitLab

1. Go to **GitLab** → **User Settings** → **Applications** (or Group/Instance level for self-hosted).
2. Set the **Redirect URI** to `https://<your-domain>/accounts/gitlab/login/callback/`.
3. Select scopes: `read_user`, `email`.
4. Copy the **Application ID** and **Secret**.

### 2. Configure in Django Admin

1. Log in to the Django admin at `/admin/`.
2. Go to **Sites** → update the default site to match your domain (e.g. `yourdomain.com`).
3. Go to **Social Applications** → **Add Social Application** for each provider:
   - **Provider**: Google / GitHub / GitLab
   - **Name**: (e.g. `Google`)
   - **Client ID**: *(value from step 1)*
   - **Secret key**: *(value from step 1)*
   - **Sites**: move your site to the **Chosen sites** column.

### 3. Environment Variables (optional via `.env`)

For self-hosted GitLab instances, add the following to your `.env`:

```env
# GitLab (only needed for self-hosted instances)
SOCIALACCOUNT_PROVIDERS_GITLAB_GITLAB_URL=https://gitlab.yourdomain.com
```

## Paid Appointment Checkout

### Environment Variables

Add the following to your `.env` (or `.envs/.local/.django` in development):

```env
# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# PayPal
PAYPAL_CLIENT_ID=...
PAYPAL_CLIENT_SECRET=...
PAYPAL_MODE=sandbox          # or "live"
PAYPAL_WEBHOOK_ID=...
PAYPAL_BRAND_NAME=Runbookly
```

### Local Webhook Testing

**Stripe CLI:**

```bash
stripe listen --forward-to http://localhost:8000/billing/webhooks/stripe/
```

Copy the `whsec_...` printed by the CLI into `STRIPE_WEBHOOK_SECRET`.

**PayPal sandbox:**

Use the PayPal Developer Dashboard to create a sandbox webhook pointing to your
tunnel URL (e.g. from `ngrok http 8000`) at `/billing/webhooks/paypal/`.
Set `PAYPAL_WEBHOOK_ID` to the ID shown in the dashboard.

### How It Works

1. User books an appointment (slot remains unconfirmed until paid).
2. User visits `GET /billing/appointments/summary/<transaction_id>/` to pay.
3. Payment Create endpoint `POST /billing/appointments/create/` creates a
   `billing.PaymentTransaction` and redirects to Stripe Checkout or PayPal.
4. On success, the webhook (or the return-URL handler) calls
   `Appointment.confirm()` which sets `status=CONFIRMED` and `confirmed_at`.
5. Unpaid appointments stay unconfirmed; the slot can be booked by others.
