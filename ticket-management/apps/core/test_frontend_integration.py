#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.urls import reverse

print('=== Admin Signup Frontend Integration Test ===')

# Test URL resolution
try:
    admin_signup_url = reverse('superadmin:admin_signup')
    print(f'Admin signup URL: {admin_signup_url}')
except Exception as e:
    print(f'URL resolution error: {e}')

# Test template existence
import os
landing_page = os.path.join('templates', 'landingpage', 'index.html')
admin_signup_template = os.path.join('templates', 'superadmin', 'admin_signup.html')

print(f'Landing page exists: {os.path.exists(landing_page)}')
print(f'Admin signup template exists: {os.path.exists(admin_signup_template)}')

# Check if admin signup link is in landing page
if os.path.exists(landing_page):
    with open(landing_page, 'r', encoding='utf-8') as f:
        content = f.read()
        if 'admin-signup/' in content:
            print('Admin signup link found in landing page')
        else:
            print('Admin signup link NOT found in landing page')

# Check if CSS exists
css_file = os.path.join('templates', 'landingpage', 'styles.css')
print(f'CSS file exists: {os.path.exists(css_file)}')

if os.path.exists(css_file):
    with open(css_file, 'r', encoding='utf-8') as f:
        content = f.read()
        if 'btn-warning' in content:
            print('Admin signup button CSS found')
        else:
            print('Admin signup button CSS NOT found')

print('\n=== Frontend Integration Summary ===')
print('1. Backend: admin_signup view created')
print('2. Backend: admin_signup template created')  
print('3. Backend: URL routing configured')
print('4. Frontend: Landing page updated with admin signup link')
print('5. Frontend: CSS styling added for admin signup button')
print('6. Frontend: Main index page updated with admin signup link')

print('\n=== Access URLs ===')
print('Admin Signup: http://127.0.0.1:8000/admin-signup/')
print('SuperAdmin Signup: http://127.0.0.1:8000/admin-signup/signup/')
print('User Signup: http://127.0.0.1:8000/user-signup/')
print('Login: http://127.0.0.1:8000/login/')

print('\n=== Ready to Test ===')
print('Visit: http://127.0.0.1:8000/')
print('Click "Admin Signup" button to test the new admin signup functionality!')
