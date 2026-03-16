"""
Template context processors for currency and other global variables
"""

from django.conf import settings


def currency_context(request):
    """
    Add currency information to all templates
    """
    return {
        'CURRENCY_SYMBOL': getattr(settings, 'CURRENCY_SYMBOL', '₹'),
        'DEFAULT_CURRENCY': getattr(settings, 'DEFAULT_CURRENCY', 'INR'),
    }
