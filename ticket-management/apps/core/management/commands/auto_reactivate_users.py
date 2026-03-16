from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile

class Command(BaseCommand):
    help = 'Auto-reactivate critical users to prevent login issues'

    def handle(self, *args, **options):
        self.stdout.write("Auto-reactivating critical users...")
        self.stdout.write("=" * 50)
        
        # Critical users that must always remain active
        critical_users = [
            'pandu', 'testlogin', 'testuser', 'midhun', 
            'monika', 'sai1', 'customer1', 'customer2', 
            'customer3', 'ramesh', 'vasu', 'yash'
        ]
        
        reactivated_count = 0
        
        for username in critical_users:
            try:
                user = User.objects.get(username=username)
                user_reactivated = False
                profile_reactivated = False
                
                # Check and reactivate user if needed
                if not user.is_active:
                    user.is_active = True
                    user.save()
                    user_reactivated = True
                    reactivated_count += 1
                
                # Check and reactivate profile if needed
                try:
                    profile = user.userprofile
                    if not profile.is_active:
                        profile.is_active = True
                        profile.save()
                        profile_reactivated = True
                        reactivated_count += 1
                except UserProfile.DoesNotExist:
                    # Create profile if missing
                    from users.models import Role
                    user_role, _ = Role.objects.get_or_create(name='User')
                    UserProfile.objects.create(
                        user=user,
                        role=user_role,
                        is_active=True
                    )
                    profile_reactivated = True
                    reactivated_count += 1
                
                if user_reactivated or profile_reactivated:
                    status = "REACTIVATED"
                    if user_reactivated:
                        status += " (User)"
                    if profile_reactivated:
                        status += " (Profile)"
                    self.stdout.write(f"{username}: {status}")
                else:
                    self.stdout.write(f"{username}: Already active")
                
            except User.DoesNotExist:
                self.stdout.write(f"{username}: Not found")
        
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(f"Auto-reactivation completed: {reactivated_count} items reactivated")
        
        # Test critical logins
        self.stdout.write("\nTesting critical logins:")
        from django.contrib.auth import authenticate
        
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
        
        self.stdout.write("\nAll critical users are now ACTIVE and ready for login!")
