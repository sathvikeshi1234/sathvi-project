#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.urls import reverse

print('=== Debug Form Submission Issue ===')

client = Client()

# Test form submission with detailed debugging
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
    print(f'Has cookies: {response.cookies}')
    
    # Check if we got redirected
    if response.status_code == 302:
        print('✅ Redirect successful - checking if user was created...')
        
        # Check if user was actually created
        from django.contrib.auth.models import User
        try:
            new_user = User.objects.get(username='testadmin789')
            if new_user:
                print(f'✅ User found in database: {new_user.username}')
                print(f'✅ User email: {new_user.email}')
                print(f'✅ User is_staff: {new_user.is_staff}')
                print(f'✅ User created: {new_user.date_joined}')
                
                # Check if profile exists
                try:
                    profile = new_user.userprofile
                    if profile:
                        print(f'✅ Profile exists: {profile.role.name if profile.role else "No role"}')
                except:
                    print('❌ No profile found')
            else:
                print('❌ User not found in database')
        except User.DoesNotExist:
            print('❌ User not found in database')
            
    else:
        print('❌ No redirect or user not created')
    
except Exception as e:
    print(f'❌ Error during form submission: {e}')

print()
print('=== Analysis ===')
print('If form submission returns 200 instead of 302:')
print('1. Check if there are JavaScript errors preventing form submission')
print('2. Check if there are validation errors being returned in the response')
print('3. Check if the form action URL is correct')
print('4. Check if the admin_signup view is being called correctly')
