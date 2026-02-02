# Mobile Navbar Offcanvas Implementation

## Overview

This document describes the mobile offcanvas sidebar implementation for the tech-articles navbar.

## Features

### 1. Mobile Offcanvas Sidebar
- **Slide Animation**: Smooth right-to-left slide-in effect (300ms duration)
- **Backdrop Overlay**: Semi-transparent backdrop with blur effect
- **Body Scroll Lock**: Prevents body scrolling when offcanvas is open
- **Multiple Close Methods**:
  - Click backdrop
  - Click close button
  - Press Escape key
  - Click any navigation link
  - Resize to desktop breakpoint (1030px)

### 2. Desktop Navigation with Icons
- **Icon + Text Layout**: Each link displays an icon alongside text
- **Hover Effects**: Icons change color to primary on hover
- **Semantic Icons**:
  - Home: House icon
  - Appointments: Calendar icon
  - Articles: Document/newspaper icon
  - Resources: Book icon
  - About: Info circle icon

### 3. Menu Configuration

Menu items are directly defined in the template (`tech_articles/templates/tech-articles/home/includes/_nav.html`).

**Menu Items**:
- Home
- Appointments
- Articles
- Resources
- About

For authenticated users, an additional "Dashboard" link is available in the mobile offcanvas menu.

**Customization**:
To modify menu items, edit the template directly. Menu items appear in both:
- Desktop navigation (horizontal layout with icons)
- Mobile offcanvas sidebar (vertical layout with icons)
- Filters items based on `mobile_only` flag

### 4. Internationalization (i18n)

All menu labels use Django's translation system:
```python
from django.utils.translation import gettext_lazy as _

'label': _('Home')  # Translatable
```

JavaScript messages are also internationalized:
```javascript
const i18n = {
  openMenu: document.documentElement.lang === 'fr' ? 'Ouvrir le menu' : 'Open menu',
  closeMenu: document.documentElement.lang === 'fr' ? 'Fermer le menu' : 'Close menu'
};
```

### 5. Accessibility

#### ARIA Attributes
- `aria-expanded`: Indicates offcanvas open/closed state
- `aria-controls`: Links toggle button to offcanvas menu
- `aria-haspopup`: Indicates menu behavior
- `aria-hidden`: Hides offcanvas from screen readers when closed
- `aria-label`: Provides accessible labels for icon-only buttons

#### Keyboard Navigation
- **Escape Key**: Closes offcanvas
- **Focus Management**: Maintains proper focus order
- **Tab Navigation**: All interactive elements are keyboard accessible

## Technical Implementation

### File Structure

```
tech_articles/
├── static/
│   ├── css/
│   │   ├── includes/
│   │   │   └── home.css (mobile offcanvas styles)
│   │   └── output.css (compiled CSS)
│   └── js/
│       └── home/
│           └── navbar/
│               └── navbar.js (offcanvas behavior)
└── templates/
    └── tech-articles/
        └── home/
            └── includes/
                └── _nav.html (navbar template with menu items)
```

### CSS Classes

#### Desktop Navigation
- `.nav-link`: Base navigation link style
- `.group`: Enables group-based hover effects
- `.group-hover:text-primary`: Icon color change on hover

#### Mobile Offcanvas
- `.mobile-offcanvas-link`: Base style for offcanvas links
- `.mobile-offcanvas-link.active`: Active state styling
- Transition classes: `translate-x-full`, `translate-x-0`, `opacity-0`, `opacity-100`

### JavaScript State Management

```javascript
const STATE = {
  isOffcanvasOpen: false,  // Track offcanvas state
  lockedScrollY: 0,        // Store scroll position before lock
};
```

**Key Functions**:
- `openOffcanvas()`: Opens sidebar, locks scroll, shows backdrop
- `closeOffcanvas()`: Closes sidebar, unlocks scroll, hides backdrop
- `toggleOffcanvas()`: Toggles between open/closed states
- `lockBodyScroll()`: Prevents body scrolling
- `unlockBodyScroll()`: Restores body scrolling and position

## Configuration

### Adding a New Menu Item

1. Edit `tech_articles/templates/tech-articles/home/includes/_nav.html`
2. Add the menu item in both sections:

**Desktop Navigation** (around line 16):
```html
<a href="/new-section" class="nav-link group">
  <svg class="w-5 h-5 inline-block mr-1.5 group-hover:text-primary transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="YOUR_SVG_PATH_HERE"></path>
  </svg>
  {% trans "New Section" %}
</a>
```

**Mobile Offcanvas** (around line 276):
```html
<a href="/new-section" class="mobile-offcanvas-link group">
  <svg class="w-5 h-5 text-text-secondary group-hover:text-primary transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="YOUR_SVG_PATH_HERE"></path>
  </svg>
  <span>{% trans "New Section" %}</span>
</a>
```

### Showing Items for Authenticated Users Only

Use Django template conditionals:

```html
{% if user.is_authenticated %}
  <a href="/dashboard" class="mobile-offcanvas-link group">
    <svg>...</svg>
    <span>{% trans "Dashboard" %}</span>
  </a>
{% endif %}
```

## Browser Support

- **Modern Browsers**: Full support (Chrome, Firefox, Safari, Edge)
- **CSS Features**: Transforms, transitions, backdrop-filter
- **JavaScript Features**: ES6+, Custom Events, ResizeObserver fallback

## Performance Considerations

1. **CSS Animations**: Hardware-accelerated (transform, opacity)
2. **Event Listeners**: Passive scroll listeners for better performance
3. **No External Dependencies**: Pure vanilla JavaScript
4. **Minimal DOM Manipulation**: State managed with CSS classes

## Future Enhancements

Potential improvements for future iterations:

1. **Submenu Support**: Add nested menu items
2. **Icon Library**: Use a dedicated icon library (Heroicons, FontAwesome)
3. **Gesture Support**: Swipe gestures to open/close offcanvas
4. **Theme Switching**: Dark/light mode toggle in offcanvas
5. **Search Integration**: Add search bar in mobile offcanvas
6. **User Profile**: Show user info at top of offcanvas when authenticated

## Troubleshooting

### Offcanvas Not Sliding In

Check:
1. CSS output file is compiled and loaded
2. JavaScript file is loaded without errors
3. Element IDs match between HTML and JavaScript
4. Tailwind classes are not being purged

### Menu Items Not Showing

Check:
1. Template file is being loaded correctly
2. Template syntax is valid
3. Static files are compiled (CSS)
4. JavaScript files are loaded without errors

### Scroll Lock Not Working

Check:
1. Body position styles are being applied
2. No conflicting CSS on body element
3. `unlockBodyScroll()` is called on close

## Testing Checklist

- [ ] Desktop view shows all menu items with icons
- [ ] Mobile view shows hamburger menu button
- [ ] Clicking hamburger opens offcanvas from right
- [ ] Backdrop appears with blur effect
- [ ] Body scroll is locked when offcanvas is open
- [ ] Clicking backdrop closes offcanvas
- [ ] Clicking close button closes offcanvas
- [ ] Pressing Escape closes offcanvas
- [ ] Clicking a link closes offcanvas
- [ ] Resizing to desktop closes offcanvas
- [ ] Active link is highlighted
- [ ] Icons change color on hover (desktop)
- [ ] Authentication-required items hidden when logged out
- [ ] All labels are translated correctly
- [ ] ARIA attributes work with screen readers
- [ ] Keyboard navigation works properly
