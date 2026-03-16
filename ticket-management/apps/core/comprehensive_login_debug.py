#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User

print('=== Comprehensive Login Debug ===')

client = Client()

# Test 1: Check URL resolution
print('1. Testing URL Resolution...')
try:
    login_url = reverse('superadmin:superadmin_login')
    print(f'Login URL: {login_url}')
except Exception as e:
    print(f'URL Resolution Error: {e}')

# Test 2: Check different URL paths
urls_to_test = [
    '/superadmin/login/',
    '/superadmin/',
    '/admin/',
]

for url in urls_to_test:
    print(f'\n2. Testing URL: {url}')
    try:
        response = client.get(url)
        print(f'   GET Status: {response.status_code}')
        if response.status_code == 200:
            content = response.content.decode()
            if 'login' in content.lower():
                print('   -> This is a login page')
            if 'csrf' in content.lower():
                print('   -> Has CSRF token')
    except Exception as e:
        print(f'   Error: {e}')

# Test 3: Test login with different credentials
print('\n3. Testing Login Process...')

login_data = {
    'username': 'TestSathvika',
    'password': 'TestPass123!'
}

# Test POST to different login URLs
login_urls = [
    '/superadmin/login/',
    '/admin-login/',
    '/login/',
]

for url in login_urls:
    print(f'\n   Testing POST to: {url}')
    try:
        # Start fresh session
        client = Client()
        
        response = client.post(url, data=login_data, follow=False)
        print(f'   POST Status: {response.status_code}')
        
        if response.status_code == 302:
            redirect_url = response.get('Location')
            print(f'   Redirect to: {redirect_url}')
            
            # Follow redirect
            response = client.get(redirect_url)
            print(f'   Follow Status: {response.status_code}')
            
            if response.status_code == 200:
                content = response.content.decode()
                if 'dashboard' in content.lower():
                    print('   -> SUCCESS: Dashboard reached')
                elif 'payment' in content.lower():
                    print('   -> SUCCESS: Payment modal likely present')
                else:
                    print('   -> Unknown page reached')
            else:
                print(f'   -> Redirect failed with status: {response.status_code}')
                
        elif response.status_code == 200:
            content = response.content.decode()
            if 'error' in content.lower() or 'invalid' in content.lower():
                print('   -> Login failed with error message')
                # Extract error message
                lines = content.split('\n')
                for line in lines:
                    if 'error' in line.lower() or 'invalid' in line.lower():
                        print(f'   Error: {line.strip()[:100]}')
                        break
            else:
                print('   -> Login page returned (no redirect)')
        else:
            print(f'   -> Unexpected status: {response.status_code}')
            
    except Exception as e:
        print(f'   Error: {e}')

# Test 4: Check user authentication directly
print('\n4. Testing User Authentication...')
try:
    from django.contrib.auth import authenticate
    user = authenticate(username='TestSathvika', password='TestPass123!')
    print(f'Authentication result: {user}')
    
    if user:
        print(f'User found: {user.username}')
        print(f'Is active: {user.is_active}')
        print(f'Is staff: {user.is_staff}')
        
        # Check role
        try:
            profile = user.userprofile
            role = profile.role.name if profile.role else 'No role'
            print(f'Role: {role}')
        except:
            print('No profile found')
    else:
        print('Authentication failed')
        
except Exception as e:
    print(f'Error: {e}')

print('\n=== Debug Complete ===')
print('If login still fails, check:')
print('1. Browser developer tools (F12) -> Network tab')
print('2. Look for failed requests or error responses')
print('3. Check console for JavaScript errors')
print('4. Verify the exact URL being accessed')
