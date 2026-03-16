#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

print('=== DEBUG ADMIN SIGNUP URL ISSUE ===')

# Test 1: Check both URLs
print('\n1. TESTING DIFFERENT ADMIN SIGNUP URLS:')

from django.test import Client
client = Client()

# Test wrong URL (what user is trying)
print('\nTesting WRONG URL: http://127.0.0.1:8000/admin-signup/')
try:
    response = client.get('/admin-signup/')
    print(f'Status: {response.status_code}')
    if response.status_code == 404:
        print('ERROR: URL not found - this is the wrong URL!')
    elif response.status_code == 200:
        print('OK: This URL works but may be different view')
    else:
        print(f'Unexpected status: {response.status_code}')
except Exception as e:
    print(f'ERROR: {e}')

# Test correct URL
print('\nTesting CORRECT URL: http://127.0.0.1:8000/superadmin/admin-signup/')
try:
    response = client.get('/superadmin/admin-signup/')
    print(f'Status: {response.status_code}')
    if response.status_code == 200:
        print('OK: This is the correct admin signup URL')
        content = response.content.decode()
        if 'Create Admin Account' in content:
            print('OK: Admin signup form found')
        if 'csrf' in content.lower():
            print('OK: CSRF token present')
    else:
        print(f'ERROR: Expected 200, got {response.status_code}')
except Exception as e:
    print(f'ERROR: {e}')

# Test 2: Check URL routing
print('\n2. CHECKING URL ROUTING:')
try:
    from django.urls import reverse
    
    # Try to resolve admin_signup from different apps
    try:
        url1 = reverse('superadmin:admin_signup')
        print(f'SuperAdmin admin_signup: {url1}')
    except:
        print('ERROR: superadmin:admin_signup not found')
    
    try:
        url2 = reverse('admin_signup')
        print(f'Users admin_signup: {url2}')
    except:
        print('ERROR: admin_signup (users) not found')
    
except Exception as e:
    print(f'URL resolution error: {e}')

# Test 3: Check what's at /admin-signup/
print('\n3. WHAT IS AT /admin-signup/ ?')
try:
    response = client.get('/admin-signup/')
    if response.status_code == 200:
        content = response.content.decode()
        if 'Create Admin Account' in content:
            print('This is also an admin signup form (from users app)')
        elif 'Super Admin' in content:
            print('This might be a different admin signup')
        else:
            print('Unknown page content')
            print('First 200 chars:', content[:200])
    elif response.status_code == 404:
        print('Page not found - URL does not exist')
except Exception as e:
    print(f'Error checking /admin-signup/: {e}')

# Test 4: Test actual admin signup at correct URL
print('\n4. TESTING ADMIN SIGNUP AT CORRECT URL:')
try:
    import random
    unique_username = f'TestAdmin{random.randint(1000, 9999)}'
    signup_data = {
        'username': unique_username,
        'email': f'{unique_username}@test.com',
        'password': 'TestPass123!',
        'confirm_password': 'TestPass123!'
    }
    
    response = client.post('/superadmin/admin-signup/', data=signup_data)
    print(f'POST status: {response.status_code}')
    
    if response.status_code == 302:
        print('SUCCESS: Admin signup working at correct URL')
        redirect_url = response.get('Location')
        print(f'Redirecting to: {redirect_url}')
    elif response.status_code == 200:
        print('ERROR: Form returned - checking errors')
        content = response.content.decode()
        if 'alert' in content.lower():
            print('Error messages found in form')
        else:
            print('No clear error messages')
    else:
        print(f'Unexpected status: {response.status_code}')
        
except Exception as e:
    print(f'Error testing admin signup: {e}')

print('\n=== SOLUTION ===')
print('You are using the WRONG URL!')
print('')
print('WRONG:  http://127.0.0.1:8000/admin-signup/')
print('CORRECT: http://127.0.0.1:8000/superadmin/admin-signup/')
print('')
print('The correct URL includes /superadmin/ before admin-signup/')
print('')
print('Use this URL to create admin accounts:')
print('http://127.0.0.1:8000/superadmin/admin-signup/')
