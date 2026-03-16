import os
import sys
import django

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from users.models import UserProfile, Role

print('=== Checking renesh arya Account ===')

# Find the user
try:
    user = User.objects.filter(username='renesharya').first()
    if user:
        print(f'User found: {user.username}')
        print(f'Email: {user.email}')
        print(f'Is active: {user.is_active}')
        print(f'Is staff: {user.is_staff}')
        
        # Check profile
        profile = getattr(user, 'userprofile', None)
        if profile:
            print(f'Profile active: {profile.is_active}')
            print(f'Role: {profile.role.name if profile.role else "None"}')
        
        # Test password authentication
        print('\n=== Testing Password Authentication ===')
        
        # Try common passwords that might have been set
        test_passwords = [
            'password', 'Password', 'PASSWORD',
            'renesharya', 'renesh', 'arya',
            '123456', 'admin', 'agent',
            'test', 'temp', 'default'
        ]
        
        password_found = False
        for pwd in test_passwords:
            if user.check_password(pwd):
                print(f'SUCCESS: Password is "{pwd}"')
                print(f'Login with Username: renesharya, Password: {pwd}')
                password_found = True
                break
        
        if not password_found:
            print('No common test password matched')
            print('The password needs to be reset or set correctly')
            
            # Show how to reset password
            print('\n=== To Fix This Issue ===')
            print('Option 1: Set new password through Admin Dashboard')
            print('1. Go to Admin Dashboard -> Agents')
            print('2. Find "renesh arya" in the list')
            print('3. Click dropdown menu -> Set Password')
            print('4. Enter a new password and save')
            print('5. Use the new password to login')
            
    else:
        print('User "renesharya" not found in database')
        
except Exception as e:
    print(f'Error: {e}')
