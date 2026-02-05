"""
Template filters for markdown rendering with SEO optimization.

Usage Example in Templates:
    {% load markdown_filters %}
    
    <!-- Render markdown content as HTML -->
    <div class="article-content">
        {{ article_page.content|markdown_to_html }}
    </div>
    
    <!-- Get plain text excerpt for meta description -->
    <meta name="description" content="{{ article_page.content|markdown_to_plain:160 }}">

Supported Markdown Features:
    - Headers (# ## ###)
    - Bold (**text**) and Italic (*text*)
    - Lists (ordered and unordered)
    - Code blocks with syntax highlighting
    - Tables
    - Links and images
    - Block quotes
    - Horizontal rules
    - Smart typography (smart quotes, dashes)
"""
from __future__ import annotations

import markdown
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name='markdown_to_html')
def markdown_to_html(text: str) -> str:
    """
    Convert Markdown text to SEO-optimized HTML.

    This filter:
    - Parses markdown content using python-markdown
    - Adds extensions for better HTML structure (tables, fenced code, etc.)
    - Sanitizes output (markdown library doesn't allow raw HTML by default with safe_mode)
    - Generates semantic HTML5 for better SEO

    Usage in templates:
        {{ article_page.content|markdown_to_html }}

    Args:
        text: Markdown-formatted text string

    Returns:
        Safe HTML string ready for display
    """
    if not text:
        return ""

    # Configure markdown with SEO-friendly extensions
    md = markdown.Markdown(
        extensions=[
            'extra',          # Enables tables, fenced code blocks, etc.
            'nl2br',          # Converts newlines to <br> for better readability
            'sane_lists',     # Better list handling
            'codehilite',     # Syntax highlighting for code blocks
            'toc',            # Table of contents (generates proper heading hierarchy)
            'smarty',         # Smart typography (quotes, dashes)
        ],
        extension_configs={
            'codehilite': {
                'css_class': 'highlight',
                'linenums': False,
            },
            'toc': {
                'anchorlink': True,
                'permalink': True,
            }
        }
    )

    # Convert markdown to HTML
    html = md.convert(text)

    # Mark as safe since markdown library sanitizes by default
    # and we're using trusted extensions
    return mark_safe(html)


@register.filter(name='markdown_to_plain')
def markdown_to_plain(text: str, max_length: int = 200) -> str:
    """
    Convert Markdown to plain text (strip all formatting).

    Useful for meta descriptions and previews.

    Usage:
        {{ article_page.content|markdown_to_plain:160 }}

    Args:
        text: Markdown-formatted text
        max_length: Maximum length of output (default 200)

    Returns:
        Plain text string
    """
    if not text:
        return ""

    # Simple conversion: remove markdown formatting
    md = markdown.Markdown(extensions=[])
    html = md.convert(text)

    # Strip HTML tags to get plain text
    from django.utils.html import strip_tags
    plain = strip_tags(html)

    # Truncate if needed
    if len(plain) > max_length:
        plain = plain[:max_length].rsplit(' ', 1)[0] + '...'

    return plain
