"""
Custom template filters for newsletter emails.
"""
from django import template
from django.utils import formats, translation

register = template.Library()


@register.filter
def format_date_for_locale(date_obj, language_code=None):
    """
    Format a date object according to the specified language locale.

    Date formats by language:
    - 'fr': "lundi 15 février 2024" (French full date)
    - 'es': "lunes, 15 de febrero de 2024" (Spanish full date)
    - 'en': "Monday, February 15, 2024" (English full date)

    Args:
        date_obj: datetime object to format
        language_code: language code (e.g., 'en', 'fr', 'es')

    Returns:
        Formatted date string according to the language
    """
    if not date_obj:
        return ""

    if not language_code:
        language_code = translation.get_language()

    # Activate the language temporarily to format the date correctly
    current_language = translation.get_language()
    translation.activate(language_code)

    # Define date formats per language
    DATE_FORMATS = {
        'fr': r'l j F Y',      # lundi 15 février 2024
        'es': r'l, j \de F \de Y',  # lunes, 15 de febrero de 2024
        'en': r'l, F d, Y',    # Monday, February 15, 2024
    }

    # Get the format for the requested language, default to English
    date_format = DATE_FORMATS.get(language_code, r'l, F d, Y')

    try:
        formatted = formats.date_format(date_obj, date_format)
    except Exception:
        # Fallback to default format if something goes wrong
        formatted = formats.date_format(date_obj, r'l, F d, Y')

    # Restore original language
    translation.activate(current_language)

    return formatted

