# Featured Articles Management Feature - Installation Guide

## Overview

This document provides instructions for installing and using the Featured Articles management feature. This feature allows staff members to select up to 3 articles to be highlighted on the homepage.

## Components Added

### 1. Models
- **File**: `tech_articles/content/models.py`
- **Model**: `FeaturedArticles` with three ForeignKey fields to `Article`:
  - `first_feature`
  - `second_feature`
  - `third_feature`
- All fields are optional (nullable) and use `SET_NULL` on article deletion

### 2. Migration
- **File**: `tech_articles/content/migrations/0004_featuredarticles.py`
- Creates the `FeaturedArticles` table

### 3. Forms
- **File**: `tech_articles/content/forms/featured_articles_forms.py`
- **Form**: `FeaturedArticlesForm` with Selectize-compatible widgets
- Only shows published articles in dropdowns

### 4. Views
- **File**: `tech_articles/content/views/featured_articles_views.py`
- **View**: `FeaturedArticlesManageView` (staff-only access)
- Auto-creates singleton configuration on first access

### 5. URLs
- **File**: `tech_articles/content/urls/article_urls.py`
- **URL**: `/dashboard/content/featured-articles/`
- **Name**: `content:featured_articles_manage`

### 6. Templates
- **File**: `tech_articles/templates/tech-articles/dashboard/pages/featured_articles/manage.html`
- Includes Selectize CSS/JS and initialization
- Follows existing dashboard design patterns

### 7. JavaScript
- **File**: `tech_articles/static/js/dashboard/featured/featured-selectize.js`
- Initializes Selectize on the three article select fields
- Provides searchable dropdown functionality
- Uses Django's `gettext()` for internationalization

### 8. Admin
- **File**: `tech_articles/content/admin.py`
- Registers `FeaturedArticlesAdmin`
- Singleton pattern: only one configuration instance allowed
- Positioned in admin below Article management

### 9. Home View Integration
- **File**: `tech_articles/common/views.py`
- `HomePageView` now fetches featured articles configuration
- Adds context variables:
  - `first_featured_article`
  - `second_featured_article`
  - `third_featured_article`

### 10. Tests
- **File**: `tech_articles/content/tests/test_featured_articles.py`
- Tests for model relationships, SET_NULL behavior
- Tests for view access control (staff-only)
- Tests for home view context

## Installation Steps

### 1. Apply Database Migration

Run the migration to create the `FeaturedArticles` table:

```bash
# Using Docker (recommended)
just manage migrate

# Or directly with Python
python manage.py migrate content 0004
```

### 2. Collect Static Files (if needed)

If deploying to production, collect the new JavaScript file:

```bash
# Using Docker
just manage collectstatic --noinput

# Or directly
python manage.py collectstatic --noinput
```

### 3. Create Superuser (if not exists)

You need a staff/superuser account to access the featured articles management:

```bash
# Using Docker
just manage createsuperuser

# Or directly
python manage.py createsuperuser
```

## Usage

### Dashboard Access

1. Log in as a staff member or superuser
2. Navigate to: `/dashboard/content/featured-articles/`
3. Select up to 3 published articles from the searchable dropdowns
4. Click "Save Featured Articles"

### Admin Access

1. Log in to Django admin: `/admin/`
2. Go to "Content" > "Featured Articles"
3. Edit the configuration (only one instance exists)
4. Select articles and save

### Home Template Integration

In your home template (`tech_articles/templates/tech-articles/home/pages/index.html`), you can now use:

```django
{% if first_featured_article %}
  <article>
    <h2>{{ first_featured_article.title }}</h2>
    <p>{{ first_featured_article.summary }}</p>
    <!-- Add more fields as needed -->
  </article>
{% endif %}

{% if second_featured_article %}
  <article>
    <h2>{{ second_featured_article.title }}</h2>
    <p>{{ second_featured_article.summary }}</p>
  </article>
{% endif %}

{% if third_featured_article %}
  <article>
    <h2>{{ third_featured_article.title }}</h2>
    <p>{{ third_featured_article.summary }}</p>
  </article>
{% endif %}
```

## Technical Details

### Singleton Pattern

The `FeaturedArticles` model uses a singleton pattern:
- Only one configuration instance can exist
- Created automatically on first access
- Uses primary key = 1
- Admin prevents creation of additional instances

### Access Control

- Dashboard view requires authentication (`LoginRequiredMixin`)
- Only staff members can access (`AdminRequiredMixin`)
- Regular users receive a 403 Forbidden error

### Article Selection

- Only published articles appear in the dropdowns
- Articles are ordered by publication date (most recent first)
- All three fields are optional
- Selectize provides search functionality

### Database Behavior

- When a featured article is deleted, the corresponding field is set to NULL
- The configuration itself cannot be deleted through admin
- Supports multiple featured article configurations per environment

## Testing

Run the tests to verify the feature works correctly:

```bash
# Using Docker
just manage test tech_articles.content.tests.test_featured_articles

# Or directly
python manage.py test tech_articles.content.tests.test_featured_articles
```

### Test Coverage

- Model creation and field nullability
- SET_NULL behavior on article deletion
- View authentication and staff-only access
- Form submission and updates
- Home view context includes featured articles

## Troubleshooting

### Issue: Featured articles don't appear on homepage

**Solution**: Ensure the home template has been updated to display the featured articles using the context variables mentioned above.

### Issue: Cannot access management page

**Solution**: Verify you're logged in as a staff member:
```python
user.is_staff = True
user.save()
```

### Issue: No articles appear in dropdowns

**Solution**: Ensure you have published articles:
```python
Article.objects.filter(status='published').count()
```

### Issue: Migration fails

**Solution**: Check for conflicts with existing migrations and run:
```bash
python manage.py migrate content --fake 0004
python manage.py migrate content
```

## Security Considerations

1. **Staff-Only Access**: Only authenticated staff members can manage featured articles
2. **CSRF Protection**: All forms include CSRF tokens
3. **Input Validation**: Django form validation ensures only valid article IDs are accepted
4. **XSS Prevention**: All output is escaped by Django templates

## Internationalization

- All user-facing strings use `gettext_lazy` for translation
- JavaScript uses Django's `gettext()` function
- Supports all languages configured in Django settings

## Performance Notes

- Featured articles are fetched on each home page load
- Consider adding caching for high-traffic sites:

```python
from django.core.cache import cache

def get_featured_articles():
    key = 'featured_articles_config'
    config = cache.get(key)
    if config is None:
        config, _ = FeaturedArticles.objects.get_or_create(pk=1)
        cache.set(key, config, 3600)  # Cache for 1 hour
    return config
```

## Future Enhancements

Potential improvements for future versions:

1. Add featured article preview images
2. Support multiple featured article sets (e.g., by category or language)
3. Add scheduling (start/end dates for featured articles)
4. Add analytics tracking for featured article clicks
5. Support drag-and-drop reordering in the dashboard

## Support

For issues or questions, please:
1. Check the troubleshooting section above
2. Review the test cases for usage examples
3. Open an issue on the project repository

---

**Version**: 1.0  
**Last Updated**: February 16, 2026  
**Author**: GitHub Copilot Agent
