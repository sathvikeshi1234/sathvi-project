from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from users.models import UserProfile

class Command(BaseCommand):
    help = 'Permanently fix user activation issues'

    def handle(self, *args, **options):
        self.stdout.write("Permanently fixing user activation issues...")
        self.stdout.write("=" * 50)
        
        # Critical users that must always remain active
        critical_users = [
            'pandu',
            'testlogin', 
            'testuser',
            'midhun',
            'monika',
            'sai1',
            'customer1'
        ]
        
        for username in critical_users:
            try:
                user = User.objects.get(username=username)
                
                # Force activate user
                if not user.is_active:
                    user.is_active = True
                    user.save()
                    self.stdout.write(f"Activated user: {username}")
                
                # Force activate profile
                try:
                    profile = user.userprofile
                    if not profile.is_active:
                        profile.is_active = True
                        profile.save()
                        self.stdout.write(f"Activated profile: {username}")
                except UserProfile.DoesNotExist:
                    # Create profile if missing
                    from users.models import Role
                    user_role, _ = Role.objects.get_or_create(name='User')
                    UserProfile.objects.create(
                        user=user,
                        role=user_role,
                        is_active=True
                    )
                    self.stdout.write(f"Created profile: {username}")
                
                self.stdout.write(f"OK {username} - User: {user.is_active}, Profile: {user.userprofile.is_active}")
                
            except User.DoesNotExist:
                self.stdout.write(f"User not found: {username}")
        
        # Check for any other inactive users
        inactive_users = User.objects.filter(is_active=False)
        if inactive_users:
            self.stdout.write(f"\nFound {inactive_users.count()} inactive users:")
            for user in inactive_users:
                self.stdout.write(f"  - {user.username}")
                
                # Auto-fix common users
                if user.username in ['admin', 'superadmin', 'agent']:
                    user.is_active = True
                    user.save()
                    try:
                        profile = user.userprofile
                        profile.is_active = True
                        profile.save()
                    except UserProfile.DoesNotExist:
                        pass
                    self.stdout.write(f"Auto-activated: {user.username}")
        
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("User activation fix completed!")
        
        # Test critical logins
        self.stdout.write("\nTesting critical logins:")
        test_credentials = [
            ('pandu', 'password'),
            ('testlogin', 'test123'),
            ('testuser', 'testpass123'),
        ]
        
        for username, password in test_credentials:
            auth_user = authenticate(username=username, password=password)
            if auth_user:
                self.stdout.write(f"OK {username}: Login SUCCESS")
            else:
                self.stdout.write(f"FAIL {username}: Login FAILED")
