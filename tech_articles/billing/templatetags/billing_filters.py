"""
Custom template filters for billing app.
"""
from django import template
from django.utils.translation import gettext as _

from tech_articles.billing.models import Plan

register = template.Library()


@register.filter
def format_field_name(value):
    """
    Get the internationalized verbose name for a Plan model field.
    
    Uses the verbose_name defined in the Plan model for proper internationalization.
    Falls back to a formatted version of the field name if not found in the model.
    
    Example:
        'name' -> 'name' (from model verbose_name)
        'is_active' -> 'is active' (from model verbose_name)
        'custom_interval_count' -> 'custom interval count' (from model verbose_name)
    """
    if not value:
        return ""
    
    # Build a dictionary mapping field names to their verbose names from the Plan model
    field_verbose_names = {}
    for field in Plan._meta.get_fields():
        if hasattr(field, 'verbose_name'):
            field_verbose_names[field.name] = str(field.verbose_name)
    
    # Return the verbose name if found, otherwise format the field name
    if value in field_verbose_names:
        return field_verbose_names[value].capitalize()
    
    # Fallback: format the field name
    return value.replace("_", " ").capitalize()
