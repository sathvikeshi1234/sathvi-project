#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import UserProfile, Role

print('=== Admin Signup Debug ===')

# Check the admin_signup function exists
try:
    from superadmin.views import admin_signup
    print('Admin signup view exists')
except ImportError as e:
    print(f'admin_signup view not found: {e}')

# Check the URL pattern
try:
    from django.urls import reverse
    admin_signup_url = reverse('superadmin:admin_signup')
    print(f'admin_signup URL: {admin_signup_url}')
except Exception as e:
    print(f'admin_signup URL error: {e}')

# Check if template exists
import os
template_path = os.path.join('templates', 'superadmin', 'admin_signup.html')
if os.path.exists(template_path):
    print(f'admin_signup template exists: {template_path}')
else:
    print(f'admin_signup template missing: {template_path}')

# Check current Admin users
admin_role = Role.objects.filter(name='Admin').first()
if admin_role:
    admin_users = UserProfile.objects.filter(role=admin_role)
    print(f'Current Admin users: {admin_users.count()}')
    for profile in admin_users:
        print(f'  - {profile.user.username} ({profile.user.email})')

# Test creating a new admin user manually
print('\n=== Testing Manual Admin Creation ===')
test_username = 'testadmin123'
test_email = 'testadmin123@example.com'
test_password = 'TestPass123!'

print(f'Testing creation of: {test_username}')

# Check if username exists
if User.objects.filter(username=test_username).exists():
    print('❌ Username already exists')
else:
    print('Username available')
    
# Check if email exists
if User.objects.filter(email=test_email).exists():
    print('Email already exists')
else:
    print('Email available')

# Try to create the user
try:
    if not User.objects.filter(username=test_username).exists() and not User.objects.filter(email=test_email).exists():
        user = User.objects.create_user(
            username=test_username,
            email=test_email,
            password=test_password
        )
        user.is_staff = True
        user.save()
        
        # Assign Admin role
        role, _ = Role.objects.get_or_create(name='Admin')
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.role = role
        profile.save()
        
        print(f'Test admin created: {user.username}')
        print(f'Role assigned: {profile.role.name}')
        print(f'Staff status: {user.is_staff}')
        
        # Clean up test user
        user.delete()
        print('Test user cleaned up')
    else:
        print('Cannot create test admin - user/email exists')
        
except Exception as e:
    print(f'Error creating test admin: {e}')

print('\n=== Common Issues ===')
print('1. Form validation errors (missing fields, password mismatch)')
print('2. Database constraint violations')
print('3. Template rendering errors')
print('4. URL routing issues')
print('5. CSRF token issues')

print('\n=== Debug Steps ===')
print('1. Open browser dev tools (F12)')
print('2. Go to Network tab')
print('3. Try submitting admin signup form')
print('4. Check for any error responses')
print('5. Check console for JavaScript errors')
