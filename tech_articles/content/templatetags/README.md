# Markdown Template Filters

This module provides Django template filters for rendering markdown content with SEO optimization.

## Installation

The markdown library is already included in the project dependencies (`markdown==3.7`).

## Usage

### Basic Markdown Rendering

```django
{% load markdown_filters %}

<article class="prose prose-invert max-w-none">
    {{ article_page.content|markdown_to_html }}
</article>
```

### Plain Text Extraction

For meta descriptions or previews:

```django
{% load markdown_filters %}

<!-- Meta description (max 160 chars) -->
<meta name="description" content="{{ article_page.content|markdown_to_plain:160 }}">

<!-- Preview excerpt (max 200 chars - default) -->
<p class="text-gray-400">
    {{ article_page.preview_content|markdown_to_plain }}
</p>
```

## Supported Markdown Features

The `markdown_to_html` filter supports:

- **Headers**: `#`, `##`, `###` (generates proper h1, h2, h3 hierarchy)
- **Bold**: `**text**` or `__text__`
- **Italic**: `*text*` or `_text_`
- **Lists**: 
  - Unordered: `- item` or `* item`
  - Ordered: `1. item`
- **Code blocks**: 
  ```python
  def hello():
      print("Hello, World!")
  ```
- **Inline code**: `` `code` ``
- **Tables**: Full markdown table support
- **Links**: `[text](url)`
- **Images**: `![alt](url)`
- **Block quotes**: `> quote`
- **Horizontal rules**: `---` or `***`
- **Smart typography**: Automatically converts quotes, dashes, and ellipses

## SEO Extensions

The following markdown extensions are enabled for SEO optimization:

1. **extra**: Tables, fenced code blocks, and more
2. **nl2br**: Converts newlines to `<br>` tags
3. **sane_lists**: Better list handling
4. **codehilite**: Syntax highlighting for code blocks
5. **toc**: Generates table of contents with proper heading hierarchy
6. **smarty**: Smart typography (quotes, dashes, ellipses)

## Security

- HTML output is automatically sanitized by the markdown library
- No raw HTML injection is allowed by default
- XSS protection is built-in

## Examples

### Article Page Content

```django
{% extends 'base.html' %}
{% load markdown_filters %}

{% block content %}
<article class="article-content">
    <h1>{{ article_page.title }}</h1>
    
    <!-- Render full markdown content -->
    <div class="prose prose-lg">
        {{ article_page.content|markdown_to_html }}
    </div>
</article>
{% endblock %}
```

### Article Preview Card

```django
{% load markdown_filters %}

<div class="article-card">
    <h3>{{ article.title }}</h3>
    <p class="text-gray-500">
        {{ article.pages.first.content|markdown_to_plain:200 }}
    </p>
    <a href="{% url 'article_detail' article.slug %}">Read more</a>
</div>
```

### SEO Meta Tags

```django
{% load markdown_filters %}

<head>
    <title>{{ article.title }} | Your Site</title>
    <meta name="description" content="{{ article_page.preview_content|markdown_to_plain:160 }}">
    
    <!-- Open Graph -->
    <meta property="og:title" content="{{ article.title }}">
    <meta property="og:description" content="{{ article_page.preview_content|markdown_to_plain:160 }}">
</head>
```

## Editor Integration

The markdown content is created using Toast UI Editor in the dashboard. See the page form template for implementation details.

### Editor Features

- WYSIWYG markdown editing
- Live preview
- Dark theme
- Internationalization (French, Spanish, English)
- Toolbar with common formatting options

## Performance Notes

- Markdown rendering happens at display time (not cached by default)
- Consider implementing caching for frequently accessed content
- The markdown library is efficient for typical content sizes

## Troubleshooting

### Content not rendering

Make sure you've loaded the templatetag library:
```django
{% load markdown_filters %}
```

### Styling issues

The rendered HTML uses standard semantic tags. Style them using CSS:

```css
/* Example prose styling */
.prose h1 { font-size: 2rem; font-weight: bold; }
.prose h2 { font-size: 1.5rem; font-weight: bold; }
.prose p { margin-bottom: 1rem; }
.prose code { background: #1a1a1a; padding: 0.25rem; }
```

Or use Tailwind's typography plugin:
```html
<div class="prose prose-invert prose-lg">
    {{ content|markdown_to_html }}
</div>
```
