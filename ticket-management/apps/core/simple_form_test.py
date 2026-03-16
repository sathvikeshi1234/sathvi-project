#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.urls import reverse

print('=== Simple Form Test ===')

client = Client()

# Test form submission
form_data = {
    'username': 'testadmin789',
    'email': 'testadmin789@example.com',
    'password': 'TestPass123!',
    'confirm_password': 'TestPass123!'
}

print('Testing form submission...')
print(f'Form data: {form_data}')

try:
    response = client.post(reverse('superadmin:admin_signup'), data=form_data, follow=False)
    print(f'Status code: {response.status_code}')
    print(f'Redirect location: {response.get("Location")}')
    
    if response.status_code == 302:
        print('SUCCESS: Form submission works - user redirected to login page')
        
        # Check if user was created
        from django.contrib.auth.models import User
        try:
            new_user = User.objects.get(username='testadmin789')
            if new_user:
                print(f'User created: {new_user.username}')
            else:
                print('User not found')
        except Exception as e:
            print(f'Error checking user: {e}')
            
    else:
        print(f'ISSUE: Form submission returned status {response.status_code}')
        print(f'Response content: {response.content[:200]}')
        
except Exception as e:
    print(f'Error: {e}')

print()
print('=== Manual Test Instructions ===')
print('1. Open browser: http://127.0.0.1:8000/admin-signup/')
print('2. Fill form and submit')
print('3. Check if you get redirected to: http://127.0.0.1:8000/superadmin/login/')
print('4. If redirected, admin signup is working!')
print('5. If not redirected, check browser console for errors')
