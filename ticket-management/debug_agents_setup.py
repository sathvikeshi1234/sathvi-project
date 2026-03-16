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

print('=== Agent Users ===')
agents = User.objects.filter(userprofile__role__name='Agent')
for agent in agents:
    print(f'Username: {agent.username}, Email: {agent.email}, Active: {agent.is_active}, Staff: {agent.is_staff}')
    profile = getattr(agent, 'userprofile', None)
    if profile:
        print(f'  Profile Active: {profile.is_active}, Role: {profile.role.name if profile.role else "None"}')
    print('---')
print(f'Total agents: {agents.count()}')

# Test authentication with a sample agent if any exist
if agents.exists():
    test_agent = agents.first()
    print(f'\n=== Testing Agent Authentication ===')
    print(f'Testing agent: {test_agent.username}')
    print(f'User exists: {User.objects.filter(username=test_agent.username).exists()}')
    
    # Try to authenticate with common test passwords
    common_passwords = ['password', '123456', 'admin', 'agent', 'test', 'temp123']
    for pwd in common_passwords:
        if test_agent.check_password(pwd):
            print(f'Password found: {pwd}')
            break
    else:
        print('No common test password matched')
