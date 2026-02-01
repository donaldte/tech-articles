"""
Template tags for dashboard sidebar menu management.
Provides utilities for determining active menu states.
"""
from django import template
from django.urls import reverse, NoReverseMatch

register = template.Library()


@register.simple_tag(takes_context=True)
def is_active(context, *url_names, **kwargs):
    """
    Check if current path matches any of the given URL names.

    Usage:
        {% is_active 'dashboard:home' as is_home_active %}
        {% is_active 'dashboard:articles_list' 'dashboard:articles_create' as is_articles_active %}

    Args:
        context: Template context containing request
        *url_names: One or more URL names to check against current path
        **kwargs: Optional URL kwargs for reverse()

    Returns:
        bool: True if current path matches any URL name
    """
    request = context.get('request')
    if not request:
        return False

    current_path = request.path

    for url_name in url_names:
        try:
            url = reverse(url_name)
            if current_path == url or current_path.startswith(url.rstrip('/') + '/'):
                return True
        except NoReverseMatch:
            continue

    return False


@register.simple_tag(takes_context=True)
def menu_item_class(context, *url_names, base_class='menu-item group'):
    """
    Returns the appropriate CSS class for a menu item based on active state.

    Usage:
        <a href="..." class="{% menu_item_class 'dashboard:home' %}">

    Args:
        context: Template context containing request
        *url_names: URL names to check for active state
        base_class: Base CSS class to include

    Returns:
        str: Full CSS class string with active/inactive modifier
    """
    request = context.get('request')
    if not request:
        return f'{base_class} menu-item-inactive'

    current_path = request.path
    is_active = False

    for url_name in url_names:
        try:
            url = reverse(url_name)
            if current_path == url or current_path.startswith(url.rstrip('/') + '/'):
                is_active = True
                break
        except NoReverseMatch:
            continue

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
        *url_names: URL names to check for active state
        prefix: CSS class prefix

    Returns:
        str: Icon CSS class with active/inactive modifier
    """
    request = context.get('request')
    if not request:
        return f'{prefix}-inactive'

    current_path = request.path
    is_active = False

    for url_name in url_names:
        try:
            url = reverse(url_name)
            if current_path == url or current_path.startswith(url.rstrip('/') + '/'):
                is_active = True
                break
        except NoReverseMatch:
            continue

    state = 'active' if is_active else 'inactive'
    return f'{prefix}-{state}'


@register.simple_tag(takes_context=True)
def menu_arrow_class(context, *url_names, prefix='menu-item-arrow'):
    """
    Returns the appropriate CSS class for a menu arrow based on active state.

    Usage:
        <svg class="{% menu_arrow_class 'dashboard:articles_list' %}">
    """
    request = context.get('request')
    if not request:
        return f'{prefix} {prefix}-inactive'

    current_path = request.path
    is_active = False

    for url_name in url_names:
        try:
            url = reverse(url_name)
            if current_path == url or current_path.startswith(url.rstrip('/') + '/'):
                is_active = True
                break
        except NoReverseMatch:
            continue

    state = 'active' if is_active else 'inactive'
    return f'{prefix} {prefix}-{state}'


@register.simple_tag(takes_context=True)
def dropdown_item_class(context, url_name, base_class='menu-dropdown-item group'):
    """
    Returns the appropriate CSS class for a dropdown menu item.

    Usage:
        <a href="..." class="{% dropdown_item_class 'dashboard:articles_create' %}">
    """
    request = context.get('request')
    if not request:
        return f'{base_class} menu-dropdown-item-inactive'

    current_path = request.path
    is_active = False

    try:
        url = reverse(url_name)
        if current_path == url:
            is_active = True
    except NoReverseMatch:
        pass

    state = 'active' if is_active else 'inactive'
    return f'{base_class} menu-dropdown-item-{state}'


@register.simple_tag(takes_context=True)
def dropdown_visibility(context, *url_names):
    """
    Returns 'hidden' class if none of the URLs are active, empty string otherwise.

    Usage:
        <div class="menu-dropdown-container {% dropdown_visibility 'dashboard:articles_list' 'dashboard:articles_create' %}">
    """
    request = context.get('request')
    if not request:
        return 'hidden'

    current_path = request.path

    for url_name in url_names:
        try:
            url = reverse(url_name)
            if current_path == url or current_path.startswith(url.rstrip('/') + '/'):
                return ''
        except NoReverseMatch:
            continue

    return 'hidden'
