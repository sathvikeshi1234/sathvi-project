#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User

print('=== Test Admin Signup Step by Step ===')

# Clean up test user
try:
    User.objects.filter(username='testadmin789').delete()
    print('Cleaned up test user')
except:
    pass

client = Client()

# Get the admin signup URL
url = reverse('superadmin:admin_signup')
print(f'Admin signup URL: {url}')

# Test form submission with debugging
form_data = {
    'username': 'testadmin789',
    'email': 'testadmin789@example.com',
    'password': 'TestPass123!',
    'confirm_password': 'TestPass123!'
}

print(f'\nSubmitting form with data: {form_data}')

# Submit the form
response = client.post(url, data=form_data, follow=False)
print(f'Response status: {response.status_code}')

if response.status_code == 200:
    print('Form returned to same page - checking for errors...')
    
    # Check response content for error messages
    content = response.content.decode()
    
    if 'Username is required' in content:
        print('ERROR: Username is required')
    elif 'Username already taken' in content:
        print('ERROR: Username already taken')
    elif 'Email already in use' in content:
        print('ERROR: Email already in use')
    elif 'Passwords do not match' in content:
        print('ERROR: Passwords do not match')
    else:
        print('No obvious error message found')
        print('Checking if user was created anyway...')
        
        try:
            user = User.objects.get(username='testadmin789')
            print(f'User found: {user.username}')
            print(f'User email: {user.email}')
            print(f'User is_staff: {user.is_staff}')
            print('User was created but form did not redirect - this is the issue!')
        except User.DoesNotExist:
            print('User was not created')
            
elif response.status_code == 302:
    print('SUCCESS: Form submitted and redirected')
    print(f'Redirect to: {response.get("Location")}')
    
    # Check if user was created
    try:
        user = User.objects.get(username='testadmin789')
        print(f'User created: {user.username}')
        print(f'User email: {user.email}')
        print(f'User is_staff: {user.is_staff}')
        print('Admin signup is working correctly!')
    except User.DoesNotExist:
        print('User not found')
else:
    print(f'Unexpected status: {response.status_code}')

print('\n=== Manual Test ===')
print('Please try this in your browser:')
print('1. Go to: http://127.0.0.1:8000/admin-signup/')
print('2. Fill in:')
print('   - Username: testadmin789')
print('   - Email: testadmin789@example.com')
print('   - Password: TestPass123!')
print('   - Confirm: TestPass123!')
print('3. Click "Create Admin Account"')
print('4. Check if you see any error messages on the page')
print('5. Check browser console (F12) for JavaScript errors')
print('6. Check Network tab to see the request details')
