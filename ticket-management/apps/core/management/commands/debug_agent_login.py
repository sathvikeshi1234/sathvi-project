from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile, Role
from django.contrib.auth import authenticate

class Command(BaseCommand):
    help = 'Debug agent login flow for inactive users'

    def handle(self, *args, **options):
        self.stdout.write("=== Debugging Agent Login Flow ===\n")
        
        # Create or get agent role
        agent_role, created = Role.objects.get_or_create(name='Agent')
        if created:
            self.stdout.write("Created Agent role")
        
        # Create test agent user
        test_username = "debug_inactive_agent"
        test_email = "debug_inactive_agent@example.com"
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
        self.stdout.write(f"Created test agent user: {test_username}")
        
        # Create user profile with Agent role and INACTIVE status
        profile, created = UserProfile.objects.get_or_create(
            user=test_user,
            defaults={'role': agent_role, 'is_active': False}
        )
        if not created:
            profile.role = agent_role
            profile.is_active = False
            profile.save()
        
        self.stdout.write("Set agent profile to INACTIVE status")
        
        # Test authentication step by step
        self.stdout.write("\n=== Testing Authentication Flow ===")
        
        # Step 1: Test direct authentication
        self.stdout.write("Step 1: Testing authenticate() function...")
        authenticated_user = authenticate(username=test_username, password=test_password)
        
        if authenticated_user:
            self.stdout.write(f"  SUCCESS: Authentication returned user")
            self.stdout.write(f"  - User.is_active: {authenticated_user.is_active}")
            self.stdout.write(f"  - User.is_staff: {authenticated_user.is_staff}")
            
            # Check UserProfile
            user_profile = getattr(authenticated_user, 'userprofile', None)
            if user_profile:
                self.stdout.write(f"  - UserProfile.is_active: {user_profile.is_active}")
                self.stdout.write(f"  - UserProfile.role: {user_profile.role}")
                self.stdout.write(f"  - Should show 'Agent account is inactive': {not user_profile.is_active}")
            else:
                self.stdout.write("  ERROR: No UserProfile found")
                
        else:
            self.stdout.write("  ERROR: Authentication returned None")
            self.stdout.write("  This means the password is wrong or user doesn't exist")
            self.stdout.write("  If this happens, the login flow will show 'Invalid username or password'")
        
        # Step 2: Test the exact logic from agent_login_view
        self.stdout.write("\nStep 2: Testing agent_login_view logic...")
        
        # Simulate the email lookup logic
        username = test_username
        lookup_username = username
        
        if '@' in username:
            try:
                email_user = User.objects.get(email=username)
                lookup_username = email_user.username
            except User.DoesNotExist:
                pass
        else:
            if not User.objects.filter(username=username).exists():
                try:
                    email_user = User.objects.get(email=username)
                    lookup_username = email_user.username
                except User.DoesNotExist:
                    pass
        
        self.stdout.write(f"  Lookup username: {lookup_username}")
        
        user = authenticate(username=lookup_username, password=test_password)
        if user:
            self.stdout.write("  User authenticated successfully")
            
            # Check if user is active (Django User field)
            if not user.is_active:
                self.stdout.write("  Would show: 'Agent account is inactive' (User.is_active is False)")
            else:
                self.stdout.write("  User.is_active is True")
            
            # Check if user profile is active (UserProfile field)
            user_profile = getattr(user, 'userprofile', None)
            if user_profile and not user_profile.is_active:
                self.stdout.write("  Would show: 'Agent account is inactive' (UserProfile.is_active is False)")
            elif user_profile:
                self.stdout.write("  UserProfile.is_active is True")
            else:
                self.stdout.write("  No UserProfile found")
            
            # Check if user has Agent role
            from users.views import _is_agent
            if _is_agent(user):
                self.stdout.write("  User has Agent role - would proceed to login")
            else:
                self.stdout.write("  Would show: 'Access denied. Agent role required.'")
        else:
            self.stdout.write("  Would show: 'Invalid username or password.'")
        
        # Clean up
        test_user.delete()
        self.stdout.write("\nCleaned up test user")
