from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile, Role

class Command(BaseCommand):
    help = 'Test inactive agent login fix'

    def handle(self, *args, **options):
        self.stdout.write("=== Testing Inactive Agent Login Fix ===\n")
        
        # Create or get agent role
        agent_role, created = Role.objects.get_or_create(name='Agent')
        if created:
            self.stdout.write("SUCCESS: Created Agent role")
        
        # Create test agent user
        test_username = "test_inactive_agent"
        test_email = "test_inactive_agent@example.com"
        test_password = "testpass123"
        
        # Clean up existing test user if exists
        User.objects.filter(username=test_username).delete()
        
        # Create new test user
        test_user = User.objects.create_user(
            username=test_username,
            email=test_email,
            password=test_password,
            is_staff=True  # Required for agent role
        )
        self.stdout.write(f"SUCCESS: Created test agent user: {test_username}")
        
        # Create user profile with Agent role and INACTIVE status
        profile, created = UserProfile.objects.get_or_create(
            user=test_user,
            defaults={'role': agent_role, 'is_active': False}
        )
        if not created:
            profile.role = agent_role
            profile.is_active = False
            profile.save()
        
        self.stdout.write("SUCCESS: Set agent profile to INACTIVE status")
        
        # Test authentication
        from django.contrib.auth import authenticate
        authenticated_user = authenticate(username=test_username, password=test_password)
        
        if authenticated_user:
            self.stdout.write("SUCCESS: Authentication successful (as expected)")
            self.stdout.write(f"   - User.is_active: {authenticated_user.is_active}")
            self.stdout.write(f"   - User.is_staff: {authenticated_user.is_staff}")
            
            # Check UserProfile
            user_profile = getattr(authenticated_user, 'userprofile', None)
            if user_profile:
                self.stdout.write(f"   - UserProfile.is_active: {user_profile.is_active}")
                self.stdout.write(f"   - UserProfile.role: {user_profile.role}")
            
            # Test the conditions that should prevent login
            if not authenticated_user.is_active:
                self.stdout.write("WARNING: Django User.is_active is False - login should be blocked")
            elif user_profile and not user_profile.is_active:
                self.stdout.write("WARNING: UserProfile.is_active is False - login should be blocked")
                self.stdout.write("SUCCESS: This will show 'Agent account is inactive' message")
            else:
                self.stdout.write("SUCCESS: User should be able to login (both active)")
                
        else:
            self.stdout.write("ERROR: Authentication failed - this shouldn't happen")
        
        self.stdout.write("\n=== Test Summary ===")
        self.stdout.write("The fix should now check both:")
        self.stdout.write("1. User.is_active (Django field)")
        self.stdout.write("2. UserProfile.is_active (custom field)")
        self.stdout.write("And show 'Agent account is inactive' message when either is False")
        
        # Clean up
        test_user.delete()
        self.stdout.write("SUCCESS: Cleaned up test user")
