# Markdown Rendering Quick Reference

Quick reference for using markdown template filters in your Django templates.

## Import the Filter

At the top of any template where you want to render markdown:

```django
{% load markdown_filters %}
```

## Render Markdown as HTML

```django
<!-- Full content rendering -->
<article class="prose prose-invert max-w-none">
    {{ article_page.content|markdown_to_html }}
</article>

<!-- Preview content -->
<div class="preview">
    {{ article_page.preview_content|markdown_to_html }}
</div>
```

## Get Plain Text (for SEO)

```django
<!-- Meta description (160 chars) -->
<meta name="description" content="{{ article_page.content|markdown_to_plain:160 }}">

<!-- Open Graph description -->
<meta property="og:description" content="{{ article_page.content|markdown_to_plain:160 }}">

<!-- Preview excerpt (default 200 chars) -->
<p>{{ article_page.content|markdown_to_plain }}</p>

<!-- Custom length (300 chars) -->
<p>{{ article_page.content|markdown_to_plain:300 }}</p>
```

## Example: Article Detail Page

```django
{% extends 'base.html' %}
{% load markdown_filters %}

{% block head %}
    <title>{{ article.title }} | Your Site</title>
    <meta name="description" content="{{ article_page.content|markdown_to_plain:160 }}">
{% endblock %}

{% block content %}
    <article>
        <h1>{{ article.title }}</h1>
        
        <!-- Render markdown content -->
        <div class="prose prose-lg prose-invert">
            {{ article_page.content|markdown_to_html }}
        </div>
    </article>
{% endblock %}
```

## Example: Article List with Previews

```django
{% load markdown_filters %}

<div class="articles-grid">
    {% for article in articles %}
        <div class="article-card">
            <h2>{{ article.title }}</h2>
            
            <!-- Show plain text excerpt -->
            <p class="text-gray-500">
                {{ article.pages.first.content|markdown_to_plain:150 }}
            </p>
            
            <a href="{% url 'article_detail' article.slug %}">
                Read more →
            </a>
        </div>
    {% endfor %}
</div>
```

## Example: With Tailwind Typography

```django
{% load markdown_filters %}

<!-- Full article with proper typography styling -->
<div class="prose prose-lg prose-invert max-w-none
            prose-headings:text-white 
            prose-p:text-gray-300 
            prose-a:text-blue-400 
            prose-strong:text-white
            prose-code:text-yellow-400
            prose-pre:bg-gray-900">
    {{ article_page.content|markdown_to_html }}
</div>
```

## Example: Conditional Paywall

```django
{% load markdown_filters %}

<article>
    {% if user.has_purchased_article or article.access_type == 'free' %}
        <!-- Full content for paying users -->
        <div class="prose prose-invert">
            {{ article_page.content|markdown_to_html }}
        </div>
    {% else %}
        <!-- Preview content for non-paying users -->
        <div class="prose prose-invert">
            {{ article_page.preview_content|markdown_to_html }}
        </div>
        
        <div class="paywall">
            <p>Continue reading with a subscription...</p>
            <a href="{% url 'article_purchase' article.pk %}" class="btn-primary">
                Purchase Access - {{ article.price }} {{ article.currency }}
            </a>
        </div>
    {% endif %}
</article>
```

## Styling the Output

The markdown_to_html filter generates semantic HTML. Style it with CSS:

### Basic CSS

```css
/* Custom styling */
.prose h1 { 
    font-size: 2.5rem; 
    font-weight: 700; 
    margin-bottom: 1rem;
}

.prose h2 { 
    font-size: 2rem; 
    font-weight: 600; 
    margin-top: 2rem;
    margin-bottom: 1rem;
}

.prose p { 
    margin-bottom: 1rem;
    line-height: 1.75;
}

.prose code { 
    background: #1a1a1a; 
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    font-family: 'Courier New', monospace;
}

.prose pre {
    background: #0d0d0d;
    padding: 1rem;
    border-radius: 0.5rem;
    overflow-x: auto;
}

.prose pre code {
    background: transparent;
    padding: 0;
}

.prose table {
    width: 100%;
    border-collapse: collapse;
    margin: 1rem 0;
}

.prose th, .prose td {
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: 0.5rem;
}

.prose th {
    background: #1a1a1a;
    font-weight: 600;
}

.prose blockquote {
    border-left: 4px solid #fbbf24;
    padding-left: 1rem;
    margin: 1rem 0;
    font-style: italic;
    color: #d1d5db;
}

.prose a {
    color: #60a5fa;
    text-decoration: underline;
}

.prose a:hover {
    color: #3b82f6;
}
```

### With Tailwind Typography Plugin

```html
<!-- Install: npm install @tailwindcss/typography -->

<div class="prose prose-invert prose-lg max-w-none">
    {{ content|markdown_to_html }}
</div>
```

## Common Patterns

### 1. Blog Post

```django
{% load markdown_filters %}

<article>
    <header>
        <h1>{{ post.title }}</h1>
        <time>{{ post.published_at|date:"F j, Y" }}</time>
    </header>
    
    <div class="prose prose-invert">
        {{ post.content|markdown_to_html }}
    </div>
    
    <footer>
        <p>By {{ post.author.name }}</p>
    </footer>
</article>
```

### 2. Documentation Page

```django
{% load markdown_filters %}

<div class="docs-container">
    <aside class="toc">
        <!-- Table of Contents -->
        <h3>Contents</h3>
        <!-- Generated by markdown's TOC extension -->
    </aside>
    
    <main class="prose prose-invert">
        {{ documentation.content|markdown_to_html }}
    </main>
</div>
```

### 3. Email Newsletter

```django
{% load markdown_filters %}

<!DOCTYPE html>
<html>
<head>
    <style>
        /* Email-safe inline styles */
    </style>
</head>
<body>
    <div style="max-width: 600px; margin: 0 auto;">
        {{ newsletter.content|markdown_to_html }}
    </div>
</body>
</html>
```

## Tips & Tricks

### Caching Rendered Content

```python
# In your view
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # Cache for 15 minutes
def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug)
    return render(request, 'article_detail.html', {'article': article})
```

### Pre-rendering at Save Time

```python
# In your model
from tech_articles.content.templatetags.markdown_filters import markdown_to_html

class ArticlePage(models.Model):
    content = models.TextField()
    content_html = models.TextField(blank=True)  # Cached HTML
    
    def save(self, *args, **kwargs):
        # Pre-render markdown to HTML
        self.content_html = markdown_to_html(self.content)
        super().save(*args, **kwargs)
```

Then in templates:
```django
<!-- Use pre-rendered HTML (faster) -->
<div class="prose">
    {{ article_page.content_html|safe }}
</div>
```

### Safe Subset of Markdown

For user-generated content, consider disabling certain features:

```python
# In markdown_filters.py, modify markdown_to_html:
md = markdown.Markdown(
    extensions=['extra', 'nl2br'],  # Limited extensions
    extension_configs={
        'extra': {
            'raw_html': False,  # Disable raw HTML
        }
    }
)
```

## Troubleshooting

### Content Not Rendering

**Problem**: Content shows as plain text  
**Solution**: Make sure you've loaded the filter:
```django
{% load markdown_filters %}
```

### Styling Issues

**Problem**: Content has no styling  
**Solution**: Add CSS classes or use Tailwind Typography:
```django
<div class="prose prose-invert">
    {{ content|markdown_to_html }}
</div>
```

### Special Characters

**Problem**: HTML entities appear  
**Solution**: The filter already marks content as safe. Don't use `|safe` again:
```django
<!-- Correct -->
{{ content|markdown_to_html }}

<!-- Wrong -->
{{ content|markdown_to_html|safe }}
```

## Resources

- **Python Markdown Docs**: https://python-markdown.github.io/
- **Markdown Guide**: https://www.markdownguide.org/
- **Tailwind Typography**: https://tailwindcss.com/docs/typography-plugin
- **TUI Editor Docs**: https://ui.toast.com/tui-editor

## Support

For issues or questions about markdown rendering:
1. Check the comprehensive guide: `tech_articles/content/templatetags/README.md`
2. See sample content: `docs/TUI_EDITOR_SAMPLES.md`
3. Review UI guide: `docs/TUI_EDITOR_UI_GUIDE.md`
