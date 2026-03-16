from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = 'Users'
    
    def ready(self):
        # Import signals after app is ready
        try:
            import users.signals
        except ImportError:
            # Handle case where signals.py might not exist
            pass
