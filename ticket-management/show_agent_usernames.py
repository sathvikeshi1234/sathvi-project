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

print('=== Recent Agents with Their Usernames ===')
recent_agents = User.objects.filter(userprofile__role__name='Agent').order_by('-id')[:10]
for agent in recent_agents:
    print(f'Name: {agent.get_full_name() or agent.username}')
    print(f'  Username: {agent.username}')
    print(f'  Email: {agent.email}')
    print(f'  Created: {agent.date_joined}')
    print('---')

print('\n=== How to Login ===')
print('Use the USERNAME (not email) to login:')
print('Example: username "sathvika.arikatla" with the password you set')
print('\nIf you forgot the username, check the list above or use email to find the corresponding username.')
