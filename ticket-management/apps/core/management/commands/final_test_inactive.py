from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile, Role
from django.test import Client

class Command(BaseCommand):
    help = 'Final test of inactive agent login fix'

    def handle(self, *args, **options):
        self.stdout.write("=== Final Test: Inactive Agent Login Fix ===\n")
        
        # Create or get agent role
        agent_role, created = Role.objects.get_or_create(name='Agent')
        
        # Create test agent user
        test_username = "final_test_agent"
        test_email = "final_test_agent@example.com"
        test_password = "testpass123"
        
        # Clean up existing test user if exists
        User.objects.filter(username=test_username).delete()
        
        # Create new test user
        test_user = User.objects.create_user(
            username=test_username,
            email=test_email,
            password=test_password,
            is_staff=True
        )
        
        # Create user profile with Agent role and INACTIVE status
        profile, created = UserProfile.objects.get_or_create(
            user=test_user,
            defaults={'role': agent_role, 'is_active': False}
        )
        if not created:
            profile.role = agent_role
            profile.is_active = False
            profile.save()
        
        self.stdout.write(f"Created inactive agent: {test_username}")
        self.stdout.write(f"User.is_active: {test_user.is_active}")
        self.stdout.write(f"UserProfile.is_active: {profile.is_active}")
        
        # Test login
        client = Client()
        
        self.stdout.write("\n=== Testing Agent Login ===")
        response = client.post('/agent-login/', {
            'username': test_username,
            'password': test_password
        })
        
        content = response.content.decode('utf-8')
        
        if 'Agent account is inactive' in content:
            self.stdout.write("SUCCESS: Shows 'Agent account is inactive' message")
        elif 'Invalid username or password' in content:
            self.stdout.write("FAILED: Still shows 'Invalid username or password'")
        else:
            self.stdout.write("UNKNOWN: Different message shown")
        
        # Test with active agent for comparison
        self.stdout.write("\n=== Testing Active Agent (for comparison) ===")
        profile.is_active = True
        profile.save()
        
        response = client.post('/agent-login/', {
            'username': test_username,
            'password': test_password
        })
        
        # Should redirect (302) for successful login
        if response.status_code == 302:
            self.stdout.write("SUCCESS: Active agent redirects to dashboard")
        else:
            self.stdout.write(f"Active agent status: {response.status_code}")
        
        # Test with inactive Django user
        self.stdout.write("\n=== Testing Inactive Django User ===")
        test_user.is_active = False
        test_user.save()
        profile.is_active = True  # Keep profile active
        profile.save()
        
        response = client.post('/agent-login/', {
            'username': test_username,
            'password': test_password
        })
        
        content = response.content.decode('utf-8')
        if 'Agent account is inactive' in content:
            self.stdout.write("SUCCESS: Shows 'Agent account is inactive' for inactive Django user")
        else:
            self.stdout.write("FAILED: Wrong message for inactive Django user")
        
        # Clean up
        test_user.delete()
        self.stdout.write("\nTest completed and cleaned up")
