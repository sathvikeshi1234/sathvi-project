#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import UserProfile, Role

print('=== Admin Signup Debug ===')

# Check if SuperAdmin already exists
superadmin_role = Role.objects.filter(name='SuperAdmin').first()
if superadmin_role:
    superadmin_profiles = UserProfile.objects.filter(role=superadmin_role)
    print(f'SuperAdmin role exists: {superadmin_role is not None}')
    print(f'SuperAdmin users: {superadmin_profiles.count()}')
    
    for profile in superadmin_profiles:
        user = profile.user
        print(f'  - {user.username} ({user.email}) - Staff: {user.is_staff} - Superuser: {user.is_superuser}')
else:
    print('SuperAdmin role does not exist')

# Check Django superusers
django_superusers = User.objects.filter(is_superuser=True)
print(f'Django superusers: {django_superusers.count()}')
for su in django_superusers:
    print(f'  - {su.username} ({su.email})')

# Check staff users
staff_users = User.objects.filter(is_staff=True)
print(f'Staff users: {staff_users.count()}')
for staff in staff_users:
    try:
        role = staff.userprofile.role.name if staff.userprofile.role else 'No role'
        print(f'  - {staff.username} ({staff.email}) - Role: {role}')
    except:
        print(f'  - {staff.username} ({staff.email}) - No profile')

print('\n=== Testing Admin Signup Logic ===')

# Simulate the check from views.py
def _has_superadmin_any():
    has_django_su = User.objects.filter(is_superuser=True).exists()
    try:
        has_role_su = User.objects.filter(userprofile__role__name='SuperAdmin').exists()
    except Exception:
        has_role_su = False
    return has_django_su or has_role_su

any_su = _has_superadmin_any()
print(f'Any SuperAdmin exists: {any_su}')

if any_su:
    print('Admin signup should be BLOCKED for non-superadmins')
    print('Only existing SuperAdmin can create new SuperAdmin')
else:
    print('Admin signup should be ALLOWED (first SuperAdmin)')

print('\n=== URL Check ===')
print('Signup URL should be: http://127.0.0.1:8000/admin-signup/')
print('URL pattern: superadmin/signup/')
print('Named URL: superadmin:superadmin_signup')
