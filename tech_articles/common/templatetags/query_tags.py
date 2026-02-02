"""
Template tags for query parameter manipulation.
Provides utilities for URL query string transformations.
"""
from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def query_transform(context, *args, **kwargs):
    """
    Tag to transform GET params from request into string for URLs.

    Accepts:
      - called without args: {% query_transform %} (uses context.request)
      - with request pos arg: {% query_transform request %}
      - with kwargs to override/add params: {% query_transform page=2 %}
      - combined: {% query_transform request page=2 %}

    Behavior:
      - merges current GET params and overrides with kwargs
      - by default removes existing 'page' param unless a 'page' kwarg is provided

    Returns a string like "?a=1&b=2" or empty string if no params.
    """
    # determine request (can be passed as first positional arg or taken from context)
    request = args[0] if args else context.get('request')
    if request is None:
        return ""

    params = request.GET.copy()

    # Apply kwargs: set or remove keys depending on value
    for k, v in kwargs.items():
        # If explicit empty/None provided, remove the key
        if v is None or v == '':
            params.pop(k, None)
        else:
            # ensure string value
            params[k] = str(v)

    # Remove existing 'page' param by default (to avoid preserving previous pagination)
    # unless the caller explicitly provided a 'page' kwarg
    if 'page' not in kwargs and 'page' in params:
        params.pop('page', None)

    return f"?{params.urlencode()}" if params else ""


@register.inclusion_tag('tech-articles/common/includes/pagination.html', takes_context=True)
def render_pagination(context, page_obj, show_info=True, adjacent_pages=2):
    """
    Render a pagination component with multiple page numbers.

    Args:
        context: Template context containing request
        page_obj: Django Page object from paginator
        show_info: Whether to show "Showing X to Y of Z results" text
        adjacent_pages: Number of pages to show on each side of current page

    Returns:
        Context dict for the pagination template
    """
    request = context.get('request')
    total_pages = page_obj.paginator.num_pages
    current_page = page_obj.number

    # Calculate page range to display
    start_page = max(current_page - adjacent_pages, 1)
    end_page = min(current_page + adjacent_pages, total_pages)

    # Adjust range if we're near the start or end
    if current_page <= adjacent_pages + 1:
        end_page = min(adjacent_pages * 2 + 1, total_pages)
    if current_page >= total_pages - adjacent_pages:
        start_page = max(total_pages - adjacent_pages * 2, 1)

    page_range = range(start_page, end_page + 1)

    # Determine if we need ellipsis
    show_first_ellipsis = start_page > 2
    show_last_ellipsis = end_page < total_pages - 1
    show_first_page = start_page > 1
    show_last_page = end_page < total_pages

    return {
        'request': request,
        'page_obj': page_obj,
        'page_range': page_range,
        'show_info': show_info,
        'show_first_page': show_first_page,
        'show_first_ellipsis': show_first_ellipsis,
        'show_last_ellipsis': show_last_ellipsis,
        'show_last_page': show_last_page,
    }
