import os
import sys
import django

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import UserProfile, Role

# Create a test agent with known password
print('=== Creating Test Agent ===')

try:
    # Get or create Agent role
    agent_role, created = Role.objects.get_or_create(name='Agent')
    if created:
        print('Created Agent role')
    
    # Create test user
    test_username = 'testagent123'
    test_email = 'testagent123@example.com'
    test_password = 'Test@123456'
    
    # Check if user already exists
    if User.objects.filter(username=test_username).exists():
        print('Test agent already exists, updating password...')
        user = User.objects.get(username=test_username)
        user.set_password(test_password)
        user.save()
    else:
        print('Creating new test agent...')
        user = User.objects.create_user(
            username=test_username,
            email=test_email,
            password=test_password,
            first_name='Test',
            last_name='Agent'
        )
        user.is_staff = True
        user.save()
        
        # Create user profile
        profile = UserProfile.objects.create(
            user=user,
            role=agent_role,
            department='Support',
            is_active=True
        )
    
    print(f'SUCCESS: Test agent created/updated:')
    print(f'   Username: {test_username}')
    print(f'   Email: {test_email}')
    print(f'   Password: {test_password}')
    print(f'   Role: Agent')
    print(f'   Active: {user.is_active}')
    print(f'   Staff: {user.is_staff}')
    
    # Test authentication
    from django.contrib.auth import authenticate
    auth_user = authenticate(username=test_username, password=test_password)
    if auth_user:
        print('SUCCESS: Authentication successful!')
    else:
        print('ERROR: Authentication failed!')
        
except Exception as e:
    print(f'ERROR: {e}')
