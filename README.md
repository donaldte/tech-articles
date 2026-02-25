# tech-articles

Premium technical article platform with paid bookings, newsletters, and AWS integration.

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

License: MIT

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
