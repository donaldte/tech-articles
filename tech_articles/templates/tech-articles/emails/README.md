# Email Templates Documentation

This directory contains all email templates for the Tech Articles application, following a dark theme design inspired by Medium.

## Structure

```
emails/
├── base_email.html           # Base template for all emails (dark theme)
├── includes/                 # Reusable email components
│   ├── _button.html         # Primary CTA button
│   ├── _code.html           # OTP/verification code display
│   └── _divider.html        # Visual divider
├── accounts/                 # Authentication-related emails
│   ├── otp_signup_verification.html         # Email verification for signup
│   ├── otp_signup_verification.txt          # Plain text version
│   ├── otp_login_verification.html          # Login verification code
│   ├── otp_login_verification.txt           # Plain text version
│   ├── otp_password_reset_verification.html # Password reset code
│   └── otp_password_reset_verification.txt  # Plain text version
└── newsletter/               # Newsletter-related emails
    ├── confirmation.html     # Double opt-in confirmation
    ├── confirmation.txt      # Plain text version
    ├── welcome.html          # Welcome email after confirmation
    ├── daily_digest.html     # Daily digest of articles
    ├── article_notification.html  # New article notification
    └── campaign.html         # General campaign template
```

## Design Guidelines

### Color Palette (Dark Theme)
- **Primary Color**: `#00E5FF` (Cyan)
- **Background**: `#0F0F10` (Very dark gray)
- **Surface**: `#19191B` (Dark gray)
- **Surface Dark**: `#1E1E24` (Slightly lighter gray)
- **Text Primary**: `#FFFFFF` (White)
- **Text Secondary**: `#A0A0B0` (Light gray)
- **Text Muted**: `#6B6B80` (Gray)
- **Border**: `rgba(255, 255, 255, 0.1)` (Transparent white)

### Typography
- **Font Family**: `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', sans-serif`
- **Heading Sizes**: 28px (h1), 24px (h2), 20px (h3)
- **Body Text**: 16px
- **Small Text**: 14px
- **Line Height**: 1.5 (24px for 16px text)

### Components

#### Base Email Template
All emails extend `base_email.html` which includes:
- Responsive wrapper (max-width: 600px)
- Header with logo/brand name
- Content area
- Footer with social links and copyright
- Unsubscribe link (for newsletters)

#### Button Component
```django
{% include "tech-articles/emails/includes/_button.html" with url=button_url text=button_text %}
```

#### Code Display Component
```django
{% include "tech-articles/emails/includes/_code.html" with code=verification_code %}
```

#### Divider Component
```django
{% include "tech-articles/emails/includes/_divider.html" %}
```

## Usage

### Authentication Emails

Authentication emails are sent automatically via Celery tasks defined in `tech_articles/accounts/tasks.py`.

**Example**:
```python
from tech_articles.accounts.tasks import send_otp_email

send_otp_email.delay(
    email='user@example.com',
    purpose='signup_verification',
    code='123456',
    otp_id='otp-uuid'
)
```

### Newsletter Emails

Newsletter emails are managed through `tech_articles/newsletter/tasks.py`.

**Confirmation Email** (Double Opt-in):
```python
from tech_articles.newsletter.tasks import send_newsletter_confirmation_email

send_newsletter_confirmation_email.delay(
    subscriber_id='subscriber-uuid',
    subscriber_email='user@example.com',
    language='fr'
)
```

**Welcome Email**:
```python
from tech_articles.newsletter.tasks import send_newsletter_welcome_email

send_newsletter_welcome_email.delay(
    subscriber_id='subscriber-uuid',
    subscriber_email='user@example.com',
    language='fr'
)
```

**Daily Digest**:
```python
from tech_articles.utils.email import EmailUtil

context = {
    'current_date': timezone.now(),
    'articles': [
        {
            'title': 'Article Title',
            'excerpt': 'Short description...',
            'url': 'https://example.com/article',
            'category': 'Python',
            'reading_time': 5,
            'image_url': 'https://example.com/image.jpg',
        },
        # ... more articles
    ],
    'site_url': settings.SITE_URL,
    'subscriber_email': 'user@example.com',
    'unsubscribe_url': 'https://example.com/unsubscribe/token',
}

EmailUtil.send_email_with_template(
    template='tech-articles/emails/newsletter/daily_digest.html',
    context=context,
    receivers=['user@example.com'],
    subject='Your Daily Tech Digest'
)
```

**Article Notification**:
```python
context = {
    'article': {
        'title': 'New Article Title',
        'excerpt': 'Article description...',
        'url': 'https://example.com/article',
        'author': 'Author Name',
        'published_date': timezone.now(),
        'reading_time': 8,
        'image_url': 'https://example.com/image.jpg',
        'tags': ['Python', 'Django', 'Tutorial'],
    },
    'unsubscribe_url': 'https://example.com/unsubscribe/token',
}

EmailUtil.send_email_with_template(
    template='tech-articles/emails/newsletter/article_notification.html',
    context=context,
    receivers=['user@example.com'],
    subject=f'New article: {article_title}'
)
```

**Campaign Email**:
```python
context = {
    'campaign': {
        'subject': 'Campaign Subject',
        'title': 'Campaign Title',
        'preview_text': 'Preview text for email clients',
        'header_image': 'https://example.com/header.jpg',
        'content': '<p>Campaign content in HTML</p>',
        'cta_url': 'https://example.com/campaign',
        'cta_text': 'Learn More',
        'show_recent_articles': True,
    },
    'recent_articles': [...],
    'subscriber_email': 'user@example.com',
    'unsubscribe_url': 'https://example.com/unsubscribe/token',
}

EmailUtil.send_email_with_template(
    template='tech-articles/emails/newsletter/campaign.html',
    context=context,
    receivers=['user@example.com'],
    subject=campaign.subject
)
```

## Internationalization

All email templates support internationalization using Django's `{% trans %}` and `{% blocktrans %}` template tags.

To add translations:
1. Mark strings with `{% trans "Text" %}` or `{% blocktrans %}...{% endblocktrans %}`
2. Run `python manage.py makemessages -l fr` to generate translation files
3. Edit `.po` files in `locale/` directory
4. Run `python manage.py compilemessages` to compile translations

## Testing

To test emails locally:
1. Configure `EMAIL_BACKEND` in settings:
   ```python
   EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
   ```
2. Emails will be printed to the console instead of being sent

For visual testing:
- Use tools like [Litmus](https://www.litmus.com/) or [Email on Acid](https://www.emailonacid.com/)
- Test across different email clients (Gmail, Outlook, Apple Mail, etc.)
- Check mobile responsiveness

## Best Practices

1. **Always provide plain text versions** for better deliverability and accessibility
2. **Keep emails under 102KB** to avoid Gmail clipping
3. **Use inline CSS** for better email client compatibility (already done in templates)
4. **Test thoroughly** across different email clients
5. **Include unsubscribe links** for all marketing emails (already included)
6. **Use descriptive alt text** for images
7. **Maintain consistent branding** across all emails
8. **Follow GDPR requirements** for newsletter subscriptions (double opt-in implemented)

## Email Client Compatibility

These templates are tested and optimized for:
- Gmail (Web, iOS, Android)
- Apple Mail (macOS, iOS)
- Outlook (Web, Desktop)
- Yahoo Mail
- ProtonMail
- Thunderbird

## Future Enhancements

Potential improvements for future iterations:
- [ ] Add email preview text optimization
- [ ] Implement A/B testing templates
- [ ] Add personalization tokens
- [ ] Create more sophisticated layouts
- [ ] Add dark mode detection (prefers-color-scheme)
- [ ] Implement email analytics (open/click tracking)
- [ ] Add more component templates (tables, lists, quotes)
