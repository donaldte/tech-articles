# Newsletter Subscriber Management

This module provides a complete newsletter subscription management system with double opt-in, GDPR compliance, and administrative features.

## Features

### User-Facing Features
- **Newsletter Subscription**: Users can subscribe by providing email and preferred language
- **Double Opt-In**: Email confirmation required before activation (GDPR compliant)
- **One-Click Unsubscribe**: Easy unsubscribe via unique token in emails
- **Multi-Language Support**: French, English, and Spanish
- **GDPR Compliance**: Consent tracking, IP address logging, timestamp tracking

### Admin Features
- **Subscriber Management**: List, view, edit, and manage all subscribers
- **Advanced Filtering**: Filter by status, language, confirmation status, and search by email
- **CSV Import/Export**: Bulk import subscribers and export data
- **Engagement Tracking**: Track subscriber interactions (opens, clicks, etc.)
- **Segmentation**: Create segments and tags for targeted campaigns
- **Statistics Dashboard**: View key metrics (total, active, confirmed, bounced)

## Models

### NewsletterSubscriber
Main subscriber model with fields:
- `email`: Unique email address
- `language`: Preferred language (fr, en, es)
- `status`: Subscriber status (active, inactive, bounced, unsubscribed)
- `is_active`: Boolean flag for active subscription
- `is_confirmed`: Boolean flag for email confirmation
- `confirm_token`: Token for email confirmation (double opt-in)
- `unsub_token`: Token for one-click unsubscribe
- `consent_given_at`: GDPR consent timestamp
- `ip_address`: IP address during subscription
- `confirmed_at`: Email confirmation timestamp

### SubscriberTag
Tags for categorizing subscribers:
- `name`: Unique tag name
- `description`: Tag description
- `color`: Hex color code for visual identification

### SubscriberSegment
Segments for grouping subscribers:
- `name`: Unique segment name
- `description`: Segment description
- `subscribers`: Many-to-many relationship with subscribers
- `tags`: Many-to-many relationship with tags

### SubscriberEngagement
Track subscriber interactions:
- `subscriber`: Foreign key to subscriber
- `email_log`: Foreign key to email log (optional)
- `action`: Engagement action (opened, clicked, etc.)
- `metadata`: Additional engagement data (JSON)

### SubscriberTagAssignment
Association between subscribers and tags

## URLs

### Public URLs (User-Facing)
- `/newsletter/subscribe/` - Newsletter subscription form
- `/newsletter/subscribe/pending/` - Pending confirmation message
- `/newsletter/confirm/<token>/` - Email confirmation endpoint
- `/newsletter/unsubscribe/<token>/` - Unsubscribe endpoint
- `/newsletter/unsubscribe/success/` - Unsubscribe success message

### Admin URLs (Staff Only)
- `/newsletter/admin/subscribers/` - List all subscribers
- `/newsletter/admin/subscribers/export/` - Export subscribers to CSV
- `/newsletter/admin/subscribers/import/` - Import subscribers from CSV
- `/newsletter/admin/subscribers/<uuid>/` - View subscriber details
- `/newsletter/admin/subscribers/<uuid>/edit/` - Edit subscriber

## Usage

### Subscribing Users

1. User visits `/newsletter/subscribe/`
2. Fills form with email, language, and consent
3. System creates subscriber with `is_confirmed=False`, `is_active=False`
4. Confirmation email sent with unique token
5. User clicks confirmation link
6. Subscriber status updated to `is_confirmed=True`, `is_active=True`, `status=ACTIVE`

### Unsubscribing Users

1. User clicks unsubscribe link in email (contains unsub_token)
2. Visits `/newsletter/unsubscribe/<token>/`
3. Confirms unsubscription
4. Subscriber status updated to `is_active=False`, `status=UNSUBSCRIBED`

### Admin Management

Staff users can:
- View all subscribers with filters (status, language, confirmed)
- Search subscribers by email
- View detailed subscriber information and engagement history
- Edit subscriber details
- Import subscribers from CSV (format: email,language)
- Export all subscribers to CSV

### CSV Import Format

```csv
email,language
john@example.com,en
marie@example.com,fr
carlos@example.com,es
```

- **Required column**: `email`
- **Optional column**: `language` (defaults to `fr` if not provided)
- **Encoding**: UTF-8
- Duplicate emails are automatically skipped

## GDPR Compliance

The system includes several GDPR compliance features:

1. **Explicit Consent**: Users must check a consent checkbox before subscribing
2. **Double Opt-In**: Email confirmation required before activation
3. **Consent Tracking**: `consent_given_at` timestamp recorded
4. **IP Address Logging**: IP address stored for audit purposes
5. **One-Click Unsubscribe**: Easy unsubscribe process
6. **Data Export**: Admin can export all subscriber data
7. **Timestamps**: All actions are timestamped (created, updated, confirmed)

## Customization

### Email Templates

To implement email sending, update the `NewsletterSubscribeView` in `views.py`:

```python
from tech_articles.utils.email import send_email

# In NewsletterSubscribeView.form_valid()
send_email(
    to=subscriber.email,
    subject=_("Confirm your newsletter subscription"),
    template="newsletter/emails/confirmation.html",
    context={
        "subscriber": subscriber,
        "confirm_url": self.request.build_absolute_uri(
            reverse("newsletter:confirm", args=[subscriber.confirm_token])
        ),
    },
)
```

### Adding Custom Fields

To add custom fields to subscribers:

1. Add field to `NewsletterSubscriber` model
2. Create migration: `python manage.py makemigrations`
3. Run migration: `python manage.py migrate`
4. Update forms and templates accordingly

### Custom Engagement Actions

Track custom engagement actions:

```python
from tech_articles.newsletter.models import SubscriberEngagement

SubscriberEngagement.objects.create(
    subscriber=subscriber,
    action="custom_action",
    metadata={"key": "value"},
)
```

## Testing

Run tests:
```bash
python manage.py test tech_articles.newsletter
```

The test suite includes:
- Model tests (creation, confirmation, unsubscription)
- Form validation tests
- View tests (GET/POST requests)
- URL routing tests
- Token validation tests

## Security Considerations

1. **Tokens**: Unsubscribe and confirmation tokens are cryptographically secure
2. **CSRF Protection**: All forms include CSRF tokens
3. **Staff Only**: Admin views require staff permissions
4. **SQL Injection**: Uses Django ORM (prevents SQL injection)
5. **XSS Protection**: Templates use Django's auto-escaping

## Internationalization

The system supports multiple languages:
- French (fr) - Default
- English (en)
- Spanish (es)

All user-facing text uses Django's translation system:
```python
from django.utils.translation import gettext_lazy as _

label = _("Email address")
```

Translation files are in `locale/*/LC_MESSAGES/django.po`

To update translations:
```bash
python manage.py makemessages -l fr
python manage.py compilemessages
```

## Future Enhancements

Potential improvements:
- Automated email campaigns
- A/B testing for campaigns
- Advanced analytics and reporting
- Integration with email service providers (SendGrid, Mailchimp, etc.)
- Subscriber preferences (frequency, topics)
- Template builder for emails
- Webhook support for external integrations
