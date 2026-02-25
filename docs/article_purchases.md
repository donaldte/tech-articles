# Article Payment System

This document describes the article purchase system, which enables users to pay for individual articles using Stripe (card, Apple Pay, Google Pay) or PayPal.

> **Note:** The article purchase flow is entirely separate from the subscription flow. Both share services and models within the `billing` app but follow independent code paths.

---

## Overview

- A user can purchase a **paid article** (`access_type=paid`) from its preview page or directly via a checkout URL.
- The purchase is a **one-time payment** (no subscription).
- After a successful payment the user immediately gains full access to the article.
- Purchases are tracked in the `Purchase` model and associated `PaymentTransaction` records.

---

## Endpoints

### User-Facing (public, login required)

| Method | URL | Name | Description |
|--------|-----|------|-------------|
| GET/POST | `/billing/articles/<slug>/purchase/` | `billing:article_purchase_checkout` | Checkout page with payment method selector |
| GET | `/billing/purchases/stripe/success/` | `billing:purchase_stripe_success` | Stripe success return URL |
| GET | `/billing/purchases/paypal/return/` | `billing:purchase_paypal_return` | PayPal return URL after approval |
| GET | `/billing/purchases/<uuid>/cancel/` | `billing:purchase_cancel` | Cancel/abandon page |

### Dashboard (login required)

| Method | URL | Name | Description |
|--------|-----|------|-------------|
| GET | `/dashboard/my-articles/` | `dashboard:my_articles` | List of purchased articles |
| GET | `/dashboard/my-purchases/` | `dashboard:my_purchases` | Purchase transaction history with pagination + status filter |

### Webhooks (public, CSRF-exempt)

| Method | URL | Name | Description |
|--------|-----|------|-------------|
| POST | `/billing/webhooks/stripe/` | `billing:stripe_webhook` | Stripe webhook (shared with subscriptions) |
| POST | `/billing/webhooks/paypal/` | `billing:paypal_webhook` | PayPal webhook (shared with subscriptions) |

---

## Environment Variables

Add these to your `.env` file (see `.env-example` for a full list):

```env
# ── Stripe ──────────────────────────────────────────────────────────────────
STRIPE_SECRET_KEY=sk_live_...            # Stripe secret key
STRIPE_PUBLISHABLE_KEY=pk_live_...       # Stripe publishable key (front-end)
STRIPE_WEBHOOK_SECRET=whsec_...          # Webhook signing secret

# ── PayPal ──────────────────────────────────────────────────────────────────
PAYPAL_CLIENT_ID=...                     # PayPal app client ID
PAYPAL_CLIENT_SECRET=...                 # PayPal app client secret
PAYPAL_API_BASE_URL=https://api-m.paypal.com  # Use https://api-m.sandbox.paypal.com for sandbox
PAYPAL_WEBHOOK_ID=...                    # Webhook ID (from PayPal developer console)
PAYPAL_BRAND_NAME=Runbookly              # Brand name shown on PayPal checkout
```

---

## Webhook Configuration

### Stripe

1. Go to **Stripe Dashboard → Webhooks → Add endpoint**.
2. Set the endpoint URL to: `https://<your-domain>/billing/webhooks/stripe/`
3. Select the following events:
   - `checkout.session.completed`
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `customer.subscription.deleted` *(for subscriptions)*
   - `invoice.payment_failed` *(for subscriptions)*
4. Copy the **Signing secret** into `STRIPE_WEBHOOK_SECRET`.

Apple Pay and Google Pay are automatically available via the `card` payment method on supported browsers/devices — no extra configuration needed.

### PayPal

1. Go to **PayPal Developer Console → My Apps → Webhooks**.
2. Set the endpoint URL to: `https://<your-domain>/billing/webhooks/paypal/`
3. Subscribe to:
   - `CHECKOUT.ORDER.APPROVED`
   - `PAYMENT.CAPTURE.COMPLETED`
   - `PAYMENT.CAPTURE.DENIED`
   - `BILLING.SUBSCRIPTION.ACTIVATED` *(for subscriptions)*
   - `BILLING.SUBSCRIPTION.CANCELLED` *(for subscriptions)*
4. Copy the **Webhook ID** into `PAYPAL_WEBHOOK_ID`.

---

## Data Models

### `Purchase` (in `billing/models.py`)

| Field | Type | Description |
|-------|------|-------------|
| `user` | FK → User | Purchasing user |
| `article` | FK → Article | Purchased article |
| `provider` | CharField | `stripe` or `paypal` |
| `status` | CharField | `pending`, `succeeded`, `failed`, `cancelled` |
| `amount` | DecimalField | Purchase amount (snapshot at time of purchase) |
| `currency` | CharField | ISO 4217 currency code |
| `provider_payment_id` | CharField | Stripe session ID or PayPal order ID |

### `PaymentTransaction` (in `billing/models.py`)

Linked to a `Purchase` via `GenericForeignKey` (`content_type` + `object_id`).  
`kind` is set to `"one_time"` for article purchases.

---

## Idempotency & Concurrency

- `Purchase` has a `unique_together = [("user", "article")]` constraint — a user can have at most one purchase record per article.
- If a pending purchase already exists (e.g., user clicked back and tried again), it is **reused** rather than duplicated.
- A new `PaymentTransaction` is always created for each payment attempt.
- Webhooks check `webhook_processed = True` to skip already-processed events.
- The Stripe success return URL also confirms the purchase immediately (in case the webhook arrives late), but the webhook handler is idempotent.

---

## Access Control

After a successful purchase, the user's purchased article IDs are cached in Redis via `BillingCache.get_purchased_article_ids()`. The cache is invalidated automatically via Django signals (`post_save` on `Purchase`).

The `ArticleDetailView` checks:
1. Article is free → full access for everyone.
2. User has an active subscription → full access.
3. User has a succeeded purchase for the article → full access.
4. Otherwise → preview (paywall).
