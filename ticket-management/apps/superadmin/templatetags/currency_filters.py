from django import template

register = template.Library()

@register.filter
def currency_symbol(value):
    """Return currency symbol based on currency code"""
    currency_symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'JPY': '¥',
        'INR': '₹',
    }
    return currency_symbols.get(value, '₹')  # Default to INR

@register.filter
def currency(value):
    """Format currency value with default INR symbol"""
    if value is None:
        return "₹0.00"
    try:
        return f"₹{float(value):,.2f}"
    except (ValueError, TypeError):
        return "₹0.00"

@register.filter
def format_currency(amount, currency_code='INR'):
    """Format amount with appropriate currency symbol"""
    symbol = currency_symbol(currency_code)
    return f"{symbol}{amount:,.2f}"

@register.simple_tag
def get_currency_symbol(currency_code='INR'):
    """Get currency symbol for use in templates"""
    return currency_symbol(currency_code)
