#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.urls import reverse

print('=== Debug Frontend Form Issue ===')

client = Client()

# Get the admin signup page
url = reverse('superadmin:admin_signup')
print(f'Admin signup URL: {url}')

response = client.get(url)
print(f'GET status: {response.status_code}')

if response.status_code == 200:
    content = response.content.decode()
    
    # Check if form action is correct
    if 'action="/superadmin/admin-signup/"' in content:
        print('Form action is correct: /superadmin/admin-signup/')
    elif 'action="/admin-signup/"' in content:
        print('Form action is: /admin-signup/')
        print('This might be the issue - should be /superadmin/admin-signup/')
    else:
        print('Form action not found or incorrect')
        print('Searching for action attribute...')
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'action=' in line:
                print(f'Line {i+1}: {line.strip()}')
    
    # Check if form method is POST
    if 'method="post"' in content:
        print('Form method is correct: POST')
    else:
        print('Form method issue - not POST')
    
    # Check if CSRF token is present
    if 'csrf' in content:
        print('CSRF token is present')
    else:
        print('CSRF token missing - this could cause issues')
    
    # Check if all required fields are present
    required_fields = ['username', 'email', 'password', 'confirm_password']
    for field in required_fields:
        if f'name="{field}"' in content:
            print(f'Field {field}: Present')
        else:
            print(f'Field {field}: Missing')

print('\n=== Manual Debug Steps ===')
print('1. Open browser: http://127.0.0.1:8000/admin-signup/')
print('2. Right-click on the form and select "Inspect"')
print('3. Check the form action attribute')
print('4. Check if form method="post"')
print('5. Check if all input fields have correct name attributes')
print('6. Submit the form and check Network tab in DevTools')
print('7. Look for the request to see where it\'s being sent')

print('\n=== Possible Issues ===')
print('1. Form action pointing to wrong URL')
print('2. JavaScript preventing form submission')
print('3. Form validation errors not visible')
print('4. CSRF token issues')
print('5. Browser caching issues')
