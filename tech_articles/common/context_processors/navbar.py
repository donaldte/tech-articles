"""Context processors for navbar menu configuration."""
from django.utils.translation import gettext_lazy as _


def navbar_menu(request):
    """
    Provide navbar menu configuration with role-based permissions.
    
    Menu items are ordered and filtered based on user permissions.
    Each menu item has:
    - label: Translatable display name
    - url: URL or URL name
    - icon: SVG path data for the icon
    - permissions: List of required permissions (empty list = everyone)
    - authenticated: Whether user must be authenticated (default: False)
    """
    
    # Define menu items with order, labels, URLs, icons, and permissions
    menu_items = [
        {
            'order': 1,
            'label': _('Home'),
            'url': 'common:home',
            'icon': 'm4 12 8-8 8 8M6 10.5V19a1 1 0 0 0 1 1h3v-3a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v3h3a1 1 0 0 0 1-1v-8.5',
            'permissions': [],
            'authenticated': False,
        },
        {
            'order': 2,
            'label': _('Appointments'),
            'url': '/appointments',
            'icon': 'M16 2V6M8 2V6M3 10H21',
            'icon_rect': 'M3 4h18v18H3z',  # Additional rect element
            'permissions': [],
            'authenticated': False,
        },
        {
            'order': 3,
            'label': _('Articles'),
            'url': '/articles',
            'icon': 'M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z',
            'permissions': [],
            'authenticated': False,
        },
        {
            'order': 4,
            'label': _('Resources'),
            'url': '/resources',
            'icon': 'M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253',
            'permissions': [],
            'authenticated': False,
        },
        {
            'order': 5,
            'label': _('About'),
            'url': '#about',
            'icon': 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
            'permissions': [],
            'authenticated': False,
        },
        {
            'order': 6,
            'label': _('Dashboard'),
            'url': 'dashboard:home',
            'icon_fill': 'M4.857 3A1.857 1.857 0 0 0 3 4.857v4.286C3 10.169 3.831 11 4.857 11h4.286A1.857 1.857 0 0 0 11 9.143V4.857A1.857 1.857 0 0 0 9.143 3H4.857Zm10 0A1.857 1.857 0 0 0 13 4.857v4.286c0 1.026.831 1.857 1.857 1.857h4.286A1.857 1.857 0 0 0 21 9.143V4.857A1.857 1.857 0 0 0 19.143 3h-4.286Zm-10 10A1.857 1.857 0 0 0 3 14.857v4.286C3 20.169 3.831 21 4.857 21h4.286A1.857 1.857 0 0 0 11 19.143v-4.286A1.857 1.857 0 0 0 9.143 13H4.857Zm10 0A1.857 1.857 0 0 0 13 14.857v4.286c0 1.026.831 1.857 1.857 1.857h4.286A1.857 1.857 0 0 0 21 19.143v-4.286A1.857 1.857 0 0 0 19.143 13h-4.286Z',
            'permissions': [],
            'authenticated': True,
            'mobile_only': True,  # Only show in mobile menu
        },
    ]
    
    # Filter menu items based on user authentication and permissions
    filtered_items = []
    user = request.user
    
    for item in menu_items:
        # Check authentication requirement
        if item.get('authenticated', False) and not user.is_authenticated:
            continue
        
        # Check permissions
        required_permissions = item.get('permissions', [])
        if required_permissions:
            if not user.is_authenticated:
                continue
            if not user.has_perms(required_permissions):
                continue
        
        filtered_items.append(item)
    
    # Sort by order
    filtered_items.sort(key=lambda x: x['order'])
    
    return {
        'navbar_menu_items': filtered_items,
    }
