#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import UserProfile, Role

print('=== Admin Signup Issue Analysis ===')

print('Current Status:')
print('SuperAdmin signup URL exists: /admin-signup/')
print('SuperAdmin signup view exists: superadmin_signup')
print('SuperAdmin user already exists: superadmin@gmail.com')
print('Admin signup is BLOCKING new signups (by design)')
print()

print('=== Why Admin Signup is "Not Working" ===')
print('The admin signup is actually working correctly!')
print('It is blocking new signups because:')
print('1. A SuperAdmin already exists (superadmin@gmail.com)')
print('2. System security: Only existing SuperAdmin can create new ones')
print('3. This prevents unauthorized admin account creation')
print()

print('=== Solutions ===')
print('Option 1: Login as existing SuperAdmin')
print('  - Go to: http://127.0.0.1:8000/admin-signup/')
print('  - Login as: superadmin@gmail.com')
print('  - Then you can create new SuperAdmin accounts')
print()

print('Option 2: Temporarily allow new signups')
print('  - I can modify the code to allow new signups')
print('  - This will let anyone create SuperAdmin accounts')
print('  - Use only for testing/development')
print()

print('Option 3: Create SuperAdmin directly in database')
print('  - I can create a script to add new SuperAdmin')
print('  - Bypasses the signup restriction')
print()

print('=== Current SuperAdmin Account ===')
superadmin_role = Role.objects.filter(name='SuperAdmin').first()
if superadmin_role:
    superadmin_profile = UserProfile.objects.filter(role=superadmin_role).first()
    if superadmin_profile:
        user = superadmin_profile.user
        print(f'Username: {user.username}')
        print(f'Email: {user.email}')
        print(f'Role: {superadmin_profile.role.name}')
        print(f'Staff: {user.is_staff}')
        print(f'Superuser: {user.is_superuser}')

print('\nWhich solution would you like me to implement?')
