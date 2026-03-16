#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.urls import resolve

print('=== URL Resolution Test ===')

# Test different URLs
urls_to_test = [
    '/admin-signup/',
    '/superadmin/admin-signup/',
    '/admin-signup/signup/',
    '/superadmin/admin-signup/signup/'
]

client = Client()

for url in urls_to_test:
    print(f'\nTesting URL: {url}')
    
    try:
        # Try to resolve the URL
        resolved = resolve(url)
        print(f'Resolved to: {resolved.view_name}')
        print(f'Namespace: {resolved.namespace}')
        
        # Try to access the URL
        response = client.get(url)
        print(f'GET status: {response.status_code}')
        
        if response.status_code == 200:
            print('URL works')
        elif response.status_code == 404:
            print('URL not found (404)')
        else:
            print(f'Unexpected status: {response.status_code}')
            
    except Exception as e:
        print(f'Error: {e}')

print('\n=== URL Mapping Analysis ===')
print('Correct URL should be: http://127.0.0.1:8000/admin-signup/')
print('This maps to: superadmin:admin_signup view')

print('\n=== Common Issues ===')
print('1. Accessing wrong URL (should be /admin-signup/ not /superadmin/admin-signup/)')
print('2. Browser cache issues (try Ctrl+F5 to refresh)')
print('3. JavaScript errors preventing form submission')
print('4. Form validation errors not visible')

print('\n=== Debug Steps ===')
print('1. Make sure you are accessing: http://127.0.0.1:8000/admin-signup/')
print('2. Open browser DevTools (F12)')
print('3. Go to Network tab')
print('4. Fill and submit the form')
print('5. Check what URL the request is sent to')
print('6. Check the response status and content')
