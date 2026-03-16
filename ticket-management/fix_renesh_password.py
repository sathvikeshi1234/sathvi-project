import os
import sys
import django

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import UserProfile, Role

print('=== Setting Password for renesh arya Account ===')

try:
    user = User.objects.get(username='renesharya')
    
    # Set a new password
    new_password = 'Renesh@123'
    user.set_password(new_password)
    user.save()
    
    print(f'SUCCESS: Password set for {user.username}')
    print(f'Email: {user.email}')
    print(f'New Password: {new_password}')
    print(f'Role: Agent')
    print(f'Account is active and ready for login')
    
    # Test the authentication
    from django.contrib.auth import authenticate
    auth_user = authenticate(username='renesharya', password=new_password)
    if auth_user:
        print('Authentication test: SUCCESS')
    else:
        print('Authentication test: FAILED')
        
except Exception as e:
    print(f'Error: {e}')
