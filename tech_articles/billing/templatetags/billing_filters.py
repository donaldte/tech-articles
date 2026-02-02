"""
Custom template filters for billing app.
"""
from django import template

register = template.Library()


@register.filter
def format_field_name(value):
    """
    Format a field name by replacing underscores with spaces and capitalizing words.
    
    Example:
        custom_interval_count -> Custom Interval Count
        is_active -> Is Active
    """
    if not value:
        return ""
    
    # Replace underscores with spaces
    formatted = value.replace("_", " ")
    
    # Capitalize each word
    formatted = formatted.title()
    
    return formatted
