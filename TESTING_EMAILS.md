# Testing Email Templates Locally

This guide explains how to test the email templates in your local development environment.

## Quick Start

### 1. Console Email Backend (Simplest)

Update your local settings to print emails to console:

```python
# config/settings/local.py
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

Now when you trigger an email, it will be printed to your terminal/console instead of being sent.

### 2. File Email Backend (Save to Files)

To save emails as files for inspection:

```python
# config/settings/local.py
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = BASE_DIR / 'tmp' / 'emails'
```

Emails will be saved as `.eml` files in `tmp/emails/` directory.

### 3. Test Authentication Emails

#### A. Test Signup Verification Email

```python
# In Django shell (python manage.py shell)
from tech_articles.accounts.tasks import send_otp_email

send_otp_email(
    email='test@example.com',
    purpose='signup_verification',
    code='123456',
    otp_id='test-otp-id'
)
```

#### B. Test Login Verification Email

```python
send_otp_email(
    email='test@example.com',
    purpose='login_verification',
    code='789012',
    otp_id='test-login-id'
)
```

#### C. Test Password Reset Email

```python
send_otp_email(
    email='test@example.com',
    purpose='password_reset_verification',
    code='345678',
    otp_id='test-reset-id'
)
```

### 4. Test Newsletter Emails

#### A. Test Newsletter Confirmation (Double Opt-in)

```python
# Create a test subscriber first
from tech_articles.newsletter.models import NewsletterSubscriber
from django.utils import timezone

subscriber = NewsletterSubscriber.objects.create(
    email='test@example.com',
    language='fr',
    is_confirmed=False,
    consent_given_at=timezone.now(),
)

# Send confirmation email
from tech_articles.newsletter.tasks import send_newsletter_confirmation_email

send_newsletter_confirmation_email.delay(
    subscriber_id=str(subscriber.id),
    subscriber_email=subscriber.email,
    language='fr'
)
```

#### B. Test Welcome Email

```python
from tech_articles.newsletter.tasks import send_newsletter_welcome_email

send_newsletter_welcome_email.delay(
    subscriber_id=str(subscriber.id),
    subscriber_email=subscriber.email,
    language='fr'
)
```

#### C. Test Daily Digest

```python
from tech_articles.utils.email import EmailUtil
from django.utils import timezone

context = {
    'current_date': timezone.now(),
    'articles': [
        {
            'title': 'Building Scalable APIs with Django REST Framework',
            'excerpt': 'Learn how to create robust and scalable APIs...',
            'url': 'http://localhost:8000/articles/django-rest-api',
            'category': 'Python',
            'reading_time': 8,
            'image_url': 'https://via.placeholder.com/600x300',
        },
    ],
    'site_url': 'http://localhost:8000',
    'subscriber_email': 'test@example.com',
    'unsubscribe_url': 'http://localhost:8000/newsletter/unsubscribe/token123',
}

EmailUtil.send_email_with_template(
    template='tech-articles/emails/newsletter/daily_digest.html',
    context=context,
    receivers=['test@example.com'],
    subject='Your Daily Tech Digest'
)
```

#### D. Test Article Notification

```python
context = {
    'article': {
        'title': 'Understanding Async/Await in Python',
        'excerpt': 'Deep dive into Python async/await syntax...',
        'url': 'http://localhost:8000/articles/python-async',
        'author': 'Jane Doe',
        'published_date': timezone.now(),
        'reading_time': 12,
        'image_url': 'https://via.placeholder.com/600x400',
        'tags': ['Python', 'Async', 'Tutorial'],
    },
    'unsubscribe_url': 'http://localhost:8000/newsletter/unsubscribe/token123',
}

EmailUtil.send_email_with_template(
    template='tech-articles/emails/newsletter/article_notification.html',
    context=context,
    receivers=['test@example.com'],
    subject='New article: Understanding Async/Await in Python'
)
```

## Visual Testing

### Option 1: Using MailHog (Recommended)

MailHog is a local email testing tool with a web UI.

1. **Start MailHog** (if using Docker Compose):
```bash
docker-compose -f docker-compose.local.yml up mailhog
```

2. **Configure Django**:
```python
# config/settings/local.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False
```

3. **Open MailHog UI**: http://localhost:8025

### Option 2: Using Mailtrap

1. Sign up at https://mailtrap.io (free tier available)
2. Get your SMTP credentials
3. Configure Django:
```python
# config/settings/local.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.mailtrap.io'
EMAIL_PORT = 2525
EMAIL_HOST_USER = 'your-username'
EMAIL_HOST_PASSWORD = 'your-password'
EMAIL_USE_TLS = True
```

### Option 3: Generate HTML Previews

Use the preview generator script:

```bash
python scripts/generate_email_previews.py
```

Then open the generated HTML files in `email_previews/` directory with a browser.

## Testing Checklist

### Functionality Tests
- [ ] Authentication emails send correctly
- [ ] Newsletter confirmation flow works end-to-end
- [ ] Welcome email triggers after confirmation
- [ ] Unsubscribe links work
- [ ] All links in emails are correct

### Visual Tests
- [ ] Emails render correctly in Gmail
- [ ] Emails render correctly in Outlook
- [ ] Emails render correctly in Apple Mail
- [ ] Mobile responsive (test on phone)
- [ ] Images load properly
- [ ] Colors match design (#00E5FF primary)

### Content Tests
- [ ] French translations display correctly
- [ ] English translations display correctly
- [ ] OTP codes are clearly visible
- [ ] All text is readable
- [ ] No typos or grammar errors

### Technical Tests
- [ ] Plain text versions exist
- [ ] HTML validates (no broken tags)
- [ ] Inline CSS works
- [ ] Tables layout properly
- [ ] No console errors in email clients

## Common Issues & Solutions

### Issue: Emails not sending
**Solution**: Check your EMAIL_BACKEND setting and Celery is running.

### Issue: Images not displaying
**Solution**: Use absolute URLs (http://...) not relative paths (/static/...).

### Issue: Broken layout in Outlook
**Solution**: Ensure using table-based layouts, not flexbox or CSS Grid.

### Issue: Colors not showing
**Solution**: Use inline CSS, not classes or external stylesheets.

### Issue: French text not displaying
**Solution**: Run `python manage.py compilemessages` to compile .po files.

## Email Client Testing Tools

### Online Tools
- [Litmus](https://www.litmus.com/) - Premium, comprehensive testing
- [Email on Acid](https://www.emailonacid.com/) - Premium, detailed reports
- [Mail Tester](https://www.mail-tester.com/) - Free, spam score checking

### Browser Extensions
- [PutsMail](https://putsmail.com/) - Send test emails to yourself
- [Thunderbird](https://www.thunderbird.net/) - Free desktop client for testing

## Tips for Better Testing

1. **Test early and often** - Don't wait until the end
2. **Use real email addresses** - See how they look in your actual inbox
3. **Test on mobile** - Many users read emails on phones
4. **Check spam folders** - Ensure emails aren't flagged
5. **Validate HTML** - Use W3C validator
6. **Test unsubscribe** - Make sure it works properly
7. **Check loading times** - Keep images optimized
8. **Test dark mode** - Some clients have dark mode

## Debugging

### Enable Django Email Logging

```python
# config/settings/local.py
LOGGING = {
    'loggers': {
        'django.core.mail': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    }
}
```

### Check Celery Tasks

```bash
# Monitor Celery worker output
celery -A config.celery_app worker --loglevel=info
```

### Inspect Email Content

If using file backend, open the .eml files in an email client or text editor to inspect the raw HTML.

## Need Help?

- Review the README: `tech_articles/templates/tech-articles/emails/README.md`
- Check implementation summary: `IMPLEMENTATION_SUMMARY.md`
- Look at existing templates for examples
- Test in console backend first before visual testing
