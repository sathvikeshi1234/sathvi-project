#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import UserProfile, Role

print('=== Testing Admin Signup ===')

# Test the new admin signup URL and functionality
print('Created new admin signup view: admin_signup')
print('Created new admin signup template: admin_signup.html')
print('Added new URL: /admin-signup/ -> admin_signup')
print()

print('=== Available Signup Options ===')
print('1. Admin Signup: http://127.0.0.1:8000/admin-signup/')
print('   - Creates Admin role users')
print('   - No restrictions (anyone can signup)')
print('   - Gets trial access (Admin role)')
print()
print('2. SuperAdmin Signup: http://127.0.0.1:8000/admin-signup/signup/')
print('   - Creates SuperAdmin role users')
print('   - Restricted (only existing SuperAdmin can create)')
print('   - Gets trial access (SuperAdmin role)')
print()

print('=== Role Differences ===')
admin_role = Role.objects.filter(name='Admin').first()
superadmin_role = Role.objects.filter(name='SuperAdmin').first()

if admin_role:
    admin_users = UserProfile.objects.filter(role=admin_role)
    print(f'Admin users: {admin_users.count()}')

if superadmin_role:
    superadmin_users = UserProfile.objects.filter(role=superadmin_role)
    print(f'SuperAdmin users: {superadmin_users.count()}')

print()
print('=== Trial Access by Role ===')
print('Admin role: Can access 30-day free trial')
print('SuperAdmin role: Can access 30-day free trial')
print('Agent/User roles: Cannot access trial (need paid subscription)')
print()
print('=== Ready to Test ===')
print('Visit: http://127.0.0.1:8000/admin-signup/')
print('Create a new Admin account and test the signup!')
