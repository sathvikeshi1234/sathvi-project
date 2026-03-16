from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile, Role
from django.test import Client
from django.urls import reverse

class Command(BaseCommand):
    help = 'Test inactive agent login message display'

    def handle(self, *args, **options):
        self.stdout.write("=== Testing Inactive Agent Login Message Display ===\n")
        
        # Create or get agent role
        agent_role, created = Role.objects.get_or_create(name='Agent')
        if created:
            self.stdout.write("Created Agent role")
        
        # Create test agent user
        test_username = "test_message_agent"
        test_email = "test_message_agent@example.com"
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
        
        # Test login via HTTP request
        self.stdout.write("\n=== Testing HTTP Login Request ===")
        
        client = Client()
        
        # Get the login page first
        response = client.get('/agent-login/')
        if response.status_code == 200:
            self.stdout.write("SUCCESS: Can access agent login page")
        else:
            self.stdout.write(f"ERROR: Cannot access login page - status {response.status_code}")
        
        # Post login credentials
        response = client.post('/agent-login/', {
            'username': test_username,
            'password': test_password
        })
        
        self.stdout.write(f"Login response status: {response.status_code}")
        
        if response.status_code == 200:
            # Check if the response contains our error message
            content = response.content.decode('utf-8')
            if 'Agent account is inactive' in content:
                self.stdout.write("SUCCESS: 'Agent account is inactive' message found in response")
            elif 'Invalid username or password' in content:
                self.stdout.write("ERROR: Still showing 'Invalid username or password' instead")
            else:
                self.stdout.write("INFO: Neither error message found in response")
                self.stdout.write("Response content preview:")
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'error' in line.lower() or 'message' in line.lower():
                        self.stdout.write(f"  Line {i}: {line.strip()}")
        else:
            self.stdout.write(f"Unexpected response status: {response.status_code}")
        
        # Clean up
        test_user.delete()
        self.stdout.write("\nCleaned up test user")
