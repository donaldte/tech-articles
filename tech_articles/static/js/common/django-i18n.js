/**
 * Django i18n JavaScript utilities
 * 
 * This module provides internationalization functions similar to Django's gettext
 * that work with Django's JavaScript catalog system.
 * 
 * Usage:
 * 1. Include Django's JavaScript catalog in your template:
 *    <script src="{% url 'javascript-catalog' %}"></script>
 * 2. Include this file after the catalog
 * 3. Use gettext(), ngettext(), and interpolate() functions
 */

/**
 * Get translated string for a given message
 * @param {string} msgid - The message ID to translate
 * @returns {string} - Translated string or original if not found
 */
function gettext(msgid) {
    if (typeof django !== 'undefined' && django.gettext) {
        return django.gettext(msgid);
    }
    // Fallback if Django catalog is not loaded
    return msgid;
}

/**
 * Get plural translated string
 * @param {string} singular - Singular form
 * @param {string} plural - Plural form
 * @param {number} count - Count to determine which form to use
 * @returns {string} - Translated string based on count
 */
function ngettext(singular, plural, count) {
    if (typeof django !== 'undefined' && django.ngettext) {
        return django.ngettext(singular, plural, count);
    }
    // Simple fallback
    return count === 1 ? singular : plural;
}

/**
 * Interpolate variables into a translated string
 * @param {string} fmt - Format string with %(name)s placeholders
 * @param {Object} obj - Object with replacement values
 * @param {boolean} named - Whether to use named placeholders (default: true)
 * @returns {string} - Interpolated string
 */
function interpolate(fmt, obj, named) {
    if (typeof django !== 'undefined' && django.interpolate) {
        return django.interpolate(fmt, obj, named);
    }
    
    // Fallback interpolation
    if (named === undefined) {
        named = true;
    }
    
    if (named) {
        // Named interpolation: %(name)s
        return fmt.replace(/%\(\w+\)s/g, function(match) {
            const key = match.slice(2, -2); // Extract 'name' from '%(name)s'
            return obj[key] !== undefined ? obj[key] : match;
        });
    } else {
        // Positional interpolation: %s
        let index = 0;
        return fmt.replace(/%s/g, function() {
            return obj[index++] !== undefined ? obj[index - 1] : '%s';
        });
    }
}

/**
 * Lazy translation - returns a function that will translate when called
 * Useful for translations that need to be defined at load time but evaluated later
 * @param {string} msgid - Message ID to translate
 * @returns {Function} - Function that returns translated string when called
 */
function gettext_lazy(msgid) {
    return function() {
        return gettext(msgid);
    };
}

/**
 * Get language code
 * @returns {string} - Current language code
 */
function get_language() {
    if (typeof django !== 'undefined' && django.get_language) {
        return django.get_language();
    }
    // Fallback to document language or 'en'
    return document.documentElement.lang || 'en';
}

/**
 * Check if language is RTL (Right-to-Left)
 * @returns {boolean} - True if current language is RTL
 */
function is_rtl() {
    const rtl_languages = ['ar', 'he', 'fa', 'ur'];
    return rtl_languages.includes(get_language());
}

// Export functions for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        gettext,
        ngettext,
        interpolate,
        gettext_lazy,
        get_language,
        is_rtl
    };
}
