#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import UserProfile, Role
from superadmin.views import _is_superadmin_user

print('=== Debug Login Issue ===')

try:
    # Find the admin user
    admin_user = User.objects.get(username='TestSathvika')
    print(f'User: {admin_user.username}')
    print(f'Email: {admin_user.email}')
    print(f'Is Active: {admin_user.is_active}')
    print(f'Is Staff: {admin_user.is_staff}')
    print(f'Is Superuser: {admin_user.is_superuser}')
    
    # Check user profile and role
    try:
        profile = admin_user.userprofile
        role = profile.role.name if profile.role else 'No role'
        print(f'Profile Role: {role}')
    except:
        print('No profile found')
    
    # Test the SuperAdmin check function
    is_superadmin = _is_superadmin_user(admin_user)
    print(f'Is SuperAdmin (function check): {is_superadmin}')
    
    # Test authentication
    from django.contrib.auth import authenticate
    test_user = authenticate(username='TestSathvika', password='TestPass123!')
    print(f'Authentication test: {test_user}')
    
    if test_user:
        print('✅ Authentication works')
    else:
        print('❌ Authentication failed')
        print('Checking password hash...')
        print(f'Password hash: {admin_user.password[:50]}...')
    
    print(f'\n=== Issue Analysis ===')
    if not is_superadmin:
        print('PROBLEM: User is Admin, not SuperAdmin')
        print('SOLUTION: The login function only allows SuperAdmin users')
        print('You need to either:')
        print('1. Make user a SuperAdmin, OR')
        print('2. Update login to allow Admin users')
    
except User.DoesNotExist:
    print('TestSathvika user not found')
except Exception as e:
    print(f'Error: {e}')
