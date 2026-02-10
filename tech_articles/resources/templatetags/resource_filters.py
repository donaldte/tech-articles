"""
Template tags and filters for resources app.
"""
from django import template
from django.utils.safestring import mark_safe

from tech_articles.resources.utils.file_utils import (
    truncate_filename,
    format_file_size,
    get_file_icon_class
)

register = template.Library()


@register.filter(name='truncate_filename')
def truncate_filename_filter(filename, max_length=30):
    """
    Template filter to truncate filename intelligently.

    Usage in templates:
        {{ resource.file_name|truncate_filename }}
        {{ resource.file_name|truncate_filename:40 }}

    Args:
        filename (str): The filename to truncate
        max_length (int): Maximum length (default: 30)

    Returns:
        str: Truncated filename

    Examples:
        {{ "very_long_document_name.pdf"|truncate_filename:20 }}
        => "very_lo...me.pdf"

        {{ "document_without_extension"|truncate_filename:20 }}
        => "document_withou..."
    """
    try:
        max_length = int(max_length)
    except (ValueError, TypeError):
        max_length = 30

    return truncate_filename(filename, max_length)


@register.filter(name='filesize')
def filesize_filter(size_in_bytes):
    """
    Template filter to format file size in human-readable format.

    Usage in templates:
        {{ resource.file_size|filesize }}

    Args:
        size_in_bytes (int): Size in bytes

    Returns:
        str: Formatted file size

    Examples:
        {{ 1048576|filesize }}
        => "1.0 MB"

        {{ 1024|filesize }}
        => "1.0 KB"
    """
    return format_file_size(size_in_bytes)


@register.filter(name='file_icon')
def file_icon_filter(filename):
    """
    Template filter to get icon class based on file extension.

    Usage in templates:
        <i class="{{ resource.file_name|file_icon }}"></i>

    Args:
        filename (str): The filename

    Returns:
        str: Icon class name

    Examples:
        {{ "document.pdf"|file_icon }}
        => "file-pdf"
    """
    return get_file_icon_class(filename)


@register.simple_tag
def file_icon_svg(filename, css_class="w-6 h-6"):
    """
    Template tag to render SVG icon based on file extension.

    Usage in templates:
        {% file_icon_svg resource.file_name %}
        {% file_icon_svg resource.file_name "w-8 h-8" %}

    Args:
        filename (str): The filename
        css_class (str): CSS classes for the SVG

    Returns:
        str: SVG HTML markup
    """
    icon_type = get_file_icon_class(filename)

    # SVG icons mapping
    icons = {
        'file-pdf': '''
            <svg class="{css_class} text-red-500" fill="currentColor" viewBox="0 0 24 24">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6z"/>
                <path d="M14 2v6h6M9.5 12.5v5M11.5 14.5h-4M13 14.5h2"/>
            </svg>
        ''',
        'file-word': '''
            <svg class="{css_class} text-blue-500" fill="currentColor" viewBox="0 0 24 24">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6z"/>
                <path d="M14 2v6h6M9 13l1 4 1-4 1 4 1-4"/>
            </svg>
        ''',
        'file-excel': '''
            <svg class="{css_class} text-green-500" fill="currentColor" viewBox="0 0 24 24">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6z"/>
                <path d="M14 2v6h6M9 13l4 4M13 13l-4 4"/>
            </svg>
        ''',
        'file-powerpoint': '''
            <svg class="{css_class} text-orange-500" fill="currentColor" viewBox="0 0 24 24">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6z"/>
                <path d="M14 2v6h6M9 13h3a2 2 0 0 1 0 4H9v-4z"/>
            </svg>
        ''',
        'file-archive': '''
            <svg class="{css_class} text-yellow-500" fill="currentColor" viewBox="0 0 24 24">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6z"/>
                <path d="M14 2v6h6M10 9h1M11 11h1M10 13h1M11 15h1M10 17h1"/>
            </svg>
        ''',
        'file-image': '''
            <svg class="{css_class} text-purple-500" fill="currentColor" viewBox="0 0 24 24">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6z"/>
                <path d="M14 2v6h6M9 15l2-2 4 4"/>
                <circle cx="9.5" cy="11.5" r="1"/>
            </svg>
        ''',
        'file-text': '''
            <svg class="{css_class} text-gray-500" fill="currentColor" viewBox="0 0 24 24">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6z"/>
                <path d="M14 2v6h6M9 13h6M9 17h6"/>
            </svg>
        ''',
        'file-default': '''
            <svg class="{css_class} text-text-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
            </svg>
        '''
    }

    svg = icons.get(icon_type, icons['file-default'])
    svg = svg.format(css_class=css_class)

    return mark_safe(svg)

