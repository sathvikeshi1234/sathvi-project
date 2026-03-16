#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

print('=== Test Exact Form Submission ===')

client = Client()

# Test 1: Get login page to get CSRF token
print('1. Getting login page...')
response = client.get('/superadmin/login/')
print(f'Login page status: {response.status_code}')

if response.status_code == 200:
    # Extract CSRF token
    csrf_token = client.cookies['csrftoken'].value
    print(f'CSRF token: {csrf_token[:20]}...')
    
    # Test 2: Submit form exactly like browser
    print('\n2. Testing form submission...')
    
    form_data = {
        'username': 'TestSathvika',
        'password': 'TestPass123!',
        'csrfmiddlewaretoken': csrf_token
    }
    
    response = client.post('/superadmin/login/', data=form_data)
    print(f'Form submission status: {response.status_code}')
    
    if response.status_code == 302:
        redirect_url = response.get('Location')
        print(f'Redirect to: {redirect_url}')
        
        # Follow redirect
        dashboard_response = client.get(redirect_url)
        print(f'Dashboard status: {dashboard_response.status_code}')
        
        if dashboard_response.status_code == 200:
            content = dashboard_response.content.decode()
            if 'paymentRequiredModal' in content:
                print('SUCCESS: Modal found in dashboard!')
            else:
                print('Dashboard loaded but no modal detected')
        else:
            print('Dashboard access failed')
            
    elif response.status_code == 200:
        # Login failed - check for error messages
        content = response.content.decode()
        if 'alert' in content.lower():
            print('Login failed - error message present')
            # Extract error message
            lines = content.split('\n')
            for line in lines:
                if 'alert' in line.lower():
                    print(f'Error: {line.strip()[:100]}')
                    break
        else:
            print('Login failed but no error message visible')
    else:
        print(f'Unexpected status: {response.status_code}')

# Test 3: Try without CSRF (like some browsers)
print('\n3. Testing without CSRF token...')
client_no_csrf = Client(enforce_csrf_checks=False)
response = client_no_csrf.post('/superadmin/login/', {
    'username': 'TestSathvika',
    'password': 'TestPass123!'
})
print(f'Status without CSRF: {response.status_code}')

print('\n=== Browser Debug Instructions ===')
print('1. Open browser: http://127.0.0.1:8000/superadmin/login/')
print('2. Open Developer Tools (F12)')
print('3. Go to Network tab')
print('4. Fill form and submit')
print('5. Check the request details:')
print('   - URL: should be /superadmin/login/')
print('   - Method: POST')
print('   - Form data: username, password, csrf token')
print('   - Response: should be 302 redirect')
print('6. Check Console tab for JavaScript errors')
