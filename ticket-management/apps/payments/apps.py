"""
Django app configuration for payments
"""

from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'payments'
    verbose_name = 'Payment Processing'
    
    def ready(self):
        # Import signal handlers when app is ready
        try:
            from . import signals
        except ImportError:
            pass
