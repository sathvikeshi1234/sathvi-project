from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile

class Command(BaseCommand):
    help = 'Synchronize user and profile active status'

    def handle(self, *args, **options):
        self.stdout.write("Synchronizing user and profile status...")
        self.stdout.write("=" * 50)
        
        # Get all users with profiles
        users_with_profiles = User.objects.filter(userprofile__isnull=False)
        
        fixed_count = 0
        
        for user in users_with_profiles:
            profile = user.userprofile
            
            # Check if statuses are mismatched
            if user.is_active != profile.is_active:
                self.stdout.write(f"Mismatch found for {user.username}:")
                self.stdout.write(f"  User.is_active: {user.is_active}")
                self.stdout.write(f"  Profile.is_active: {profile.is_active}")
                
                # Synchronize to user status (admin panel controls user status)
                profile.is_active = user.is_active
                profile.save()
                
                self.stdout.write(f"  Fixed: Profile.is_active set to {user.is_active}")
                fixed_count += 1
                self.stdout.write("")
        
        # Also check for users without profiles
        users_without_profiles = User.objects.filter(userprofile__isnull=True)
        if users_without_profiles:
            self.stdout.write(f"Found {users_without_profiles.count()} users without profiles:")
            from users.models import Role
            user_role, _ = Role.objects.get_or_create(name='User')
            
            for user in users_without_profiles:
                UserProfile.objects.create(
                    user=user,
                    role=user_role,
                    is_active=user.is_active  # Match user status
                )
                self.stdout.write(f"  Created profile for {user.username}")
                fixed_count += 1
        
        self.stdout.write("=" * 50)
        self.stdout.write(f"Synchronization completed: {fixed_count} items fixed")
        
        # Test specific users
        test_users = ['pandu', 'testlogin', 'testuser']
        self.stdout.write("\nTesting critical users:")
        
        from django.contrib.auth import authenticate
        
        for username in test_users:
            try:
                user = User.objects.get(username=username)
                profile = user.userprofile
                
                self.stdout.write(f"\n{username}:")
                self.stdout.write(f"  User.is_active: {user.is_active}")
                self.stdout.write(f"  Profile.is_active: {profile.is_active}")
                
                # Test login
                auth_user = authenticate(username=username, password='password')
                if username == 'testuser':
                    auth_user = authenticate(username=username, password='testpass123')
                elif username == 'testlogin':
                    auth_user = authenticate(username=username, password='test123')
                
                if auth_user:
                    self.stdout.write(f"  Login: SUCCESS")
                else:
                    self.stdout.write(f"  Login: FAILED")
                    
            except User.DoesNotExist:
                self.stdout.write(f"  {username}: Not found")
