from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile

class Command(BaseCommand):
    help = 'Fix passwords for existing users'

    def handle(self, *args, **options):
        self.stdout.write("Fixing user passwords...")
        self.stdout.write("=" * 50)
        
        # Set passwords for key users
        user_passwords = {
            'midhun': 'password',
            'monika': 'password', 
            'sai1': 'password',
            'customer1': 'password',
            'customer2': 'password',
            'customer3': 'password',
            'ramesh': 'password',
            'vasu': 'password',
            'yash': 'password',
            'pandu': 'password',
            'siva': 'password',
            'siddu': 'password',
            'frooti': 'password',
            'frooti1': 'password',
            'sathvi1': 'password',
            'guest': 'password',
        }
        
        for username, password in user_passwords.items():
            try:
                user = User.objects.get(username=username)
                user.set_password(password)
                user.save()
                self.stdout.write(f"Set password for '{username}': {password}")
            except User.DoesNotExist:
                self.stdout.write(f"User '{username}' not found")
        
        # Create a guaranteed working test user
        test_username = "testlogin"
        test_password = "test123"
        
        if User.objects.filter(username=test_username).exists():
            user = User.objects.get(username=test_username)
            user.set_password(test_password)
            user.save()
            self.stdout.write(f"Updated password for existing test user")
        else:
            user = User.objects.create_user(
                username=test_username,
                email=f"{test_username}@test.com",
                password=test_password,
                is_active=True
            )
            
            # Create profile
            from users.models import Role
            user_role, _ = Role.objects.get_or_create(name='User')
            UserProfile.objects.get_or_create(
                user=user,
                defaults={'role': user_role, 'is_active': True}
            )
            
            self.stdout.write(f"Created new test user")
        
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("TEST CREDENTIALS:")
        self.stdout.write(f"Username: {test_username}")
        self.stdout.write(f"Password: {test_password}")
        self.stdout.write("\nOther working accounts:")
        self.stdout.write("- testuser / testpass123")
        self.stdout.write("- midhun / password")
        self.stdout.write("- monika / password")
        self.stdout.write("- sai1 / password")
        self.stdout.write("- customer1 / password")
        self.stdout.write("=" * 50)
