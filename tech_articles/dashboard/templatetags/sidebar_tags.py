"""
Template tags for dashboard sidebar menu management.
Provides utilities for determining active menu states based on URL resolver.
"""
from django import template
from django.urls import resolve, Resolver404

register = template.Library()


def get_current_view_name(request):
    """
    Get the current view name from the URL resolver.

    Returns the view name including namespace (e.g., 'dashboard:home').
    Returns None if the view cannot be resolved.
    """
    try:
        match = resolve(request.path)
        return match.view_name
    except Resolver404:
        return None


@register.simple_tag(takes_context=True)
def is_active(context, *url_names):
    """
    Check if current view name matches any of the given URL names.

    Usage:
        {% is_active 'dashboard:home' as is_home_active %}
        {% is_active 'dashboard:articles_list' 'dashboard:articles_create' as is_articles_active %}

    Args:
        context: Template context containing request
        *url_names: One or more view names to check (with namespace, e.g., 'dashboard:home')

    Returns:
        bool: True if current view name matches any provided view name
    """
    request = context.get('request')
    if not request:
        return False

    current_view_name = get_current_view_name(request)
    if not current_view_name:
        return False

    return current_view_name in url_names

@register.simple_tag(takes_context=True)
def menu_item_class(context, *url_names, base_class='menu-item group'):
    """
    Returns the appropriate CSS class for a menu item based on active state.

    Usage:
        <a href="..." class="{% menu_item_class 'dashboard:home' %}">

    Args:
        context: Template context containing request
        *url_names: View names to check for active state (with namespace)
        base_class: Base CSS class to include

    Returns:
        str: Full CSS class string with active/inactive modifier
    """
    request = context.get('request')
    if not request:
        return f'{base_class} menu-item-inactive'

    current_view_name = get_current_view_name(request)
    if not current_view_name:
        return f'{base_class} menu-item-inactive'

    is_active = current_view_name in url_names
    state = 'active' if is_active else 'inactive'
    return f'{base_class} menu-item-{state}'

@register.simple_tag(takes_context=True)
def menu_icon_class(context, *url_names, prefix='menu-item-icon'):
    """
    Returns the appropriate CSS class for a menu icon based on active state.

    Usage:
        <svg class="{% menu_icon_class 'dashboard:home' %}">

    Args:
        context: Template context containing request
        *url_names: View names to check for active state (with namespace)
        prefix: CSS class prefix

    Returns:
        str: Icon CSS class with active/inactive modifier
    """
    request = context.get('request')
    if not request:
        return f'{prefix}-inactive'

    current_view_name = get_current_view_name(request)
    if not current_view_name:
        return f'{prefix}-inactive'

    is_active = current_view_name in url_names
    state = 'active' if is_active else 'inactive'
    return f'{prefix}-{state}'

@register.simple_tag(takes_context=True)
def menu_arrow_class(context, *url_names, prefix='menu-item-arrow'):
    """
    Returns the appropriate CSS class for a menu arrow based on active state.

    Usage:
        <svg class="{% menu_arrow_class 'dashboard:articles_list' %}">

    Args:
        context: Template context containing request
        *url_names: View names to check for active state (with namespace)
        prefix: CSS class prefix

    Returns:
        str: Arrow CSS class with active/inactive modifier
    """
    request = context.get('request')
    if not request:
        return f'{prefix} {prefix}-inactive'

    current_view_name = get_current_view_name(request)
    if not current_view_name:
        return f'{prefix} {prefix}-inactive'

    is_active = current_view_name in url_names
    state = 'active' if is_active else 'inactive'
    return f'{prefix} {prefix}-{state}'

@register.simple_tag(takes_context=True)
def dropdown_item_class(context, *url_names, base_class='menu-dropdown-item group'):
    """
    Returns the appropriate CSS class for a dropdown menu item.

    Usage:
        <a href="..." class="{% dropdown_item_class 'dashboard:articles_create' %}">

    Args:
        context: Template context containing request
        *url_names: View names to check for active state (with namespace)
        base_class: Base CSS class to include

    Returns:
        str: Dropdown item CSS class with active/inactive modifier
    """
    request = context.get('request')
    if not request:
        return f'{base_class} menu-dropdown-item-inactive'

    current_view_name = get_current_view_name(request)
    if not current_view_name:
        return f'{base_class} menu-dropdown-item-inactive'

    is_active = current_view_name in url_names
    state = 'active' if is_active else 'inactive'
    return f'{base_class} menu-dropdown-item-{state}'

@register.simple_tag(takes_context=True)
def dropdown_visibility(context, *url_names):
    """
    Returns 'hidden' class if none of the view names are active, empty string otherwise.

    Usage:
        <div class="menu-dropdown-container {% dropdown_visibility 'dashboard:articles_list' 'dashboard:articles_create' %}">

    Args:
        context: Template context containing request
        *url_names: View names to check for active state (with namespace)

    Returns:
        str: 'hidden' if none active, empty string if any active
    """
    request = context.get('request')
    if not request:
        return 'hidden'

    current_view_name = get_current_view_name(request)
    if not current_view_name:
        return 'hidden'

    if current_view_name in url_names:
        return ''

    return 'hidden'


