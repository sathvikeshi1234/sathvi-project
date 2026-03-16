from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile, Role
from django.test import Client

class Command(BaseCommand):
    help = 'Debug Django User.is_active check'

    def handle(self, *args, **options):
        self.stdout.write("=== Debug Django User.is_active Check ===\n")
        
        # Create or get agent role
        agent_role, _ = Role.objects.get_or_create(name='Agent')
        
        # Create test agent user
        test_username = "debug_user_active"
        test_email = "debug_user_active@example.com"
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
        
        # Create user profile with Agent role and ACTIVE status
        profile, _ = UserProfile.objects.get_or_create(
            user=test_user,
            defaults={'role': agent_role, 'is_active': True}
        )
        
        self.stdout.write(f"Created agent: {test_username}")
        self.stdout.write(f"User.is_active: {test_user.is_active}")
        self.stdout.write(f"UserProfile.is_active: {profile.is_active}")
        
        # Test 1: Active user and active profile
        self.stdout.write("\n=== Test 1: Active User + Active Profile ===")
        test_user.is_active = True
        profile.is_active = True
        test_user.save()
        profile.save()
        
        client = Client()
        response = client.post('/agent-login/', {
            'username': test_username,
            'password': test_password
        })
        
        if response.status_code == 302:
            self.stdout.write("SUCCESS: Redirects to dashboard")
        else:
            content = response.content.decode('utf-8')
            if 'Agent account is inactive' in content:
                self.stdout.write("UNEXPECTED: Shows inactive message")
            else:
                self.stdout.write(f"UNEXPECTED: Status {response.status_code}")
        
        # Test 2: Inactive user and active profile
        self.stdout.write("\n=== Test 2: Inactive User + Active Profile ===")
        test_user.is_active = False
        profile.is_active = True
        test_user.save()
        profile.save()
        
        # Clear any existing messages
        client = Client()
        response = client.post('/agent-login/', {
            'username': test_username,
            'password': test_password
        })
        
        content = response.content.decode('utf-8')
        if 'Agent account is inactive' in content:
            self.stdout.write("SUCCESS: Shows 'Agent account is inactive'")
        elif 'Invalid username or password' in content:
            self.stdout.write("ISSUE: Shows 'Invalid username or password' instead")
        else:
            self.stdout.write(f"UNKNOWN: Different response - {response.status_code}")
        
        # Test 3: Active user and inactive profile
        self.stdout.write("\n=== Test 3: Active User + Inactive Profile ===")
        test_user.is_active = True
        profile.is_active = False
        test_user.save()
        profile.save()
        
        client = Client()
        response = client.post('/agent-login/', {
            'username': test_username,
            'password': test_password
        })
        
        content = response.content.decode('utf-8')
        if 'Agent account is inactive' in content:
            self.stdout.write("SUCCESS: Shows 'Agent account is inactive'")
        else:
            self.stdout.write("ISSUE: Does not show expected message")
        
        # Test 4: Check authentication behavior
        self.stdout.write("\n=== Test 4: Authentication Behavior ===")
        from django.contrib.auth import authenticate
        
        # Test with inactive Django user
        test_user.is_active = False
        test_user.save()
        
        auth_result = authenticate(username=test_username, password=test_password)
        if auth_result is None:
            self.stdout.write("INFO: authenticate() returns None for inactive user")
            self.stdout.write("This means Django's authenticate() blocks inactive users")
        else:
            self.stdout.write("INFO: authenticate() returns user even for inactive user")
            self.stdout.write("Our code needs to check user.is_active")
        
        # Clean up
        test_user.delete()
        self.stdout.write("\nDebug completed")
