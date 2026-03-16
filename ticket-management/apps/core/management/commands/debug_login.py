from django.core.management.base import BaseCommand
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from users.models import UserProfile

class Command(BaseCommand):
    help = 'Debug login authentication process'

    def handle(self, *args, **options):
        self.stdout.write("Debugging login authentication...")
        self.stdout.write("=" * 50)
        
        # Test specific users
        test_users = [
            ('testuser', 'testpass123'),
            ('midhun', 'password'),  # Common test password
            ('monika', 'password'),
            ('sai1', 'password'),
            ('customer1', 'password'),
        ]
        
        for username, password in test_users:
            self.stdout.write(f"\n--- Testing login for: {username} ---")
            
            try:
                user = User.objects.get(username=username)
                self.stdout.write(f"User found in database")
                self.stdout.write(f"  - Email: {user.email}")
                self.stdout.write(f"  - is_active: {user.is_active}")
                self.stdout.write(f"  - is_staff: {user.is_staff}")
                
                # Check profile
                try:
                    profile = user.userprofile
                    self.stdout.write(f"  - Profile.is_active: {profile.is_active}")
                    self.stdout.write(f"  - Role: {profile.role}")
                except UserProfile.DoesNotExist:
                    self.stdout.write(f"  - No profile found")
                
                # Test authentication
                auth_user = authenticate(username=username, password=password)
                if auth_user:
                    self.stdout.write(f"Authentication SUCCESS")
                    self.stdout.write(f"  - Auth user ID: {auth_user.id}")
                    self.stdout.write(f"  - Auth user is_active: {auth_user.is_active}")
                else:
                    self.stdout.write(f"Authentication FAILED")
                    
                    # Try with common passwords if failed
                    common_passwords = ['password', '123456', 'admin', 'test', 'test123']
                    for test_pass in common_passwords:
                        test_auth = authenticate(username=username, password=test_pass)
                        if test_auth:
                            self.stdout.write(f"Found working password: {test_pass}")
                            break
                    else:
                        self.stdout.write(f"No common passwords work")
                
            except User.DoesNotExist:
                self.stdout.write(f"User '{username}' not found in database")
        
        # Test creating a fresh test user
        self.stdout.write(f"\n--- Creating fresh test user ---")
        test_username = "debug_test_user"
        test_password = "testpass123"
        
        if User.objects.filter(username=test_username).exists():
            user = User.objects.get(username=test_username)
            self.stdout.write(f"Test user already exists")
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
            UserProfile.objects.create(
                user=user,
                role=user_role,
                is_active=True
            )
            
            self.stdout.write(f"Created fresh test user")
        
        # Test the fresh user
        auth_user = authenticate(username=test_username, password=test_password)
        if auth_user:
            self.stdout.write(f"Fresh user authentication SUCCESS")
        else:
            self.stdout.write(f"Fresh user authentication FAILED")
        
        self.stdout.write(f"\nTest credentials:")
        self.stdout.write(f"  Username: {test_username}")
        self.stdout.write(f"  Password: {test_password}")
        
        self.stdout.write("\n" + "=" * 50)
