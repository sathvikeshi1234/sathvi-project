#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.urls import reverse

print('=== Admin Signup Final Test ===')

client = Client()

try:
    url = reverse('superadmin:admin_signup')
    print(f'Admin signup URL: {url}')
    
    response = client.get(url)
    print(f'Status: {response.status_code}')
    
    if response.status_code == 200:
        print('SUCCESS: Admin signup page is accessible')
        print('Template content length:', len(response.content))
        
        # Test form submission
        form_data = {
            'username': 'testadmin123',
            'email': 'testadmin123@example.com',
            'password': 'TestPass123!',
            'confirm_password': 'TestPass123!'
        }
        
        post_response = client.post(url, data=form_data)
        print(f'POST status: {post_response.status_code}')
        
        if post_response.status_code == 302:
            print('SUCCESS: Form submission works (redirect)')
        else:
            print('ISSUE: Form submission failed')
            print('Response content:', post_response.content[:500])
            
    else:
        print(f'ISSUE: Got status {response.status_code}')
        
except Exception as e:
    print(f'ERROR: {e}')

print()
print('=== Manual Test Instructions ===')
print('1. Open browser and go to: http://127.0.0.1:8000/admin-signup/')
print('2. Fill in the form with:')
print('   - Username: testadmin123')
print('   - Email: testadmin123@example.com')
print('   - Password: TestPass123!')
print('   - Confirm: TestPass123!')
print('3. Click "Create Admin Account"')
print('4. Check if you get redirected to login page')
print('5. If it works, the admin signup is functional!')
