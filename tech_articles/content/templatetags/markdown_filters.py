"""
Template filters for markdown rendering with SEO optimization and security.

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

Security:
    - All HTML output is sanitized with bleach
    - Only safe HTML tags and attributes are allowed
    - XSS protection enabled
"""

from __future__ import annotations

import re

import bleach
import markdown
from django import template
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe

register = template.Library()

# Allowed HTML tags for bleach sanitization
ALLOWED_TAGS = list(bleach.sanitizer.ALLOWED_TAGS) + [
    "p",
    "pre",
    "code",
    "span",
    "div",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "table",
    "thead",
    "tbody",
    "tr",
    "th",
    "td",
    "hr",
    "br",
    "blockquote",
    "img",
    "input",  # task list checkboxes
]

# Allowed HTML attributes for bleach sanitization
ALLOWED_ATTRIBUTES = {
    **bleach.sanitizer.ALLOWED_ATTRIBUTES,
    "code": ["class"],  # for codehilite
    "span": ["class"],
    "div": ["class"],
    "pre": ["class"],
    "a": ["href", "title", "rel", "target", "id"],
    "img": ["src", "alt", "title"],
    "h1": ["id"],
    "h2": ["id"],
    "h3": ["id"],
    "h4": ["id"],
    "h5": ["id"],
    "h6": ["id"],
    "input": ["type", "checked", "disabled", "class"],  # task list checkboxes
    "li": ["class"],  # task-list-item class
    "ul": ["class"],  # task-list class
}

# Regex for matching task-list items (e.g. "- [x] done" or "- [ ] todo")
_TASK_LIST_RE = re.compile(
    r"^(\s*[-*+]\s+)\[(x| )\]\s", re.IGNORECASE | re.MULTILINE
)


class _TaskListPreprocessor(markdown.preprocessors.Preprocessor):
    """Convert GFM-style task-list syntax into inline ``<input>`` checkboxes."""

    def run(self, lines):
        new_lines = []
        for line in lines:
            m = _TASK_LIST_RE.match(line)
            if m:
                checked = m.group(2).lower() == "x"
                checked_attr = ' checked=""' if checked else ""
                prefix = m.group(1)
                # `rest` is markdown source text; the full output is bleach-sanitized
                # downstream so any embedded HTML in it will be stripped safely.
                rest = line[m.end():]
                line = f'{prefix}<input type="checkbox" disabled{checked_attr}> {rest}'
            new_lines.append(line)
        return new_lines


class _TaskListExtension(markdown.Extension):
    """Markdown extension that adds task-list checkbox support."""

    def extendMarkdown(self, md):
        md.preprocessors.register(_TaskListPreprocessor(md), "tasklist", 30)


@register.filter(name="markdown_to_html")
def markdown_to_html(text: str) -> str:
    """
    Convert Markdown text to secure, SEO-optimized HTML.

    This filter:
    - Parses markdown content using python-markdown
    - Adds extensions for better HTML structure (tables, fenced code, etc.)
    - Sanitizes output with bleach to prevent XSS attacks
    - Linkifies URLs automatically
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
            "extra",  # Enables tables, fenced code blocks, etc.
            "nl2br",  # Converts newlines to <br> for better readability
            "sane_lists",  # Better list handling
            "codehilite",  # Syntax highlighting for code blocks
            "toc",  # Table of contents (generates proper heading hierarchy)
            "smarty",  # Smart typography (quotes, dashes)
            _TaskListExtension(),  # GFM-style task-list checkboxes
        ],
        extension_configs={
            "codehilite": {
                "css_class": "highlight",
                "linenums": False,
                "guess_lang": False,
            },
            "toc": {
                "permalink": False,
            },
        },
    )

    # Convert markdown to HTML
    html = md.convert(text)

    # First, convert plain URLs to anchors so link attributes are visible to bleach
    html = bleach.linkify(html)

    # Sanitize HTML with bleach to prevent XSS (this also cleans the linkified anchors)
    html = bleach.clean(
        html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True
    )

    # Mark as safe since we've sanitized with bleach
    return mark_safe(html)


@register.filter(name="markdown_to_plain")
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
    plain = strip_tags(html)

    # Truncate if needed
    if len(plain) > max_length:
        plain = plain[:max_length].rsplit(" ", 1)[0] + "..."

    return plain
