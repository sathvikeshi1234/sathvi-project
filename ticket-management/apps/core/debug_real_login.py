#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from superadmin.views import is_admin_or_superadmin

print('=== Debug Real Login Issue ===')

# Test 1: Check user exists
try:
    user = User.objects.get(username='TestSathvika')
    print(f'User found: {user.username}')
    print(f'Email: {user.email}')
    print(f'Is active: {user.is_active}')
    print(f'Is staff: {user.is_staff}')
    print(f'Is superuser: {user.is_superuser}')
    
    # Check role
    try:
        profile = user.userprofile
        role = profile.role.name if profile.role else 'No role'
        print(f'Role: {role}')
    except:
        print('No profile found')
    
except User.DoesNotExist:
    print('ERROR: User TestSathvika does not exist')
    exit()

# Test 2: Test authentication directly
print('\n2. Testing authentication...')
auth_user = authenticate(username='TestSathvika', password='TestPass123!')
if auth_user:
    print(f'Authentication SUCCESS: {auth_user.username}')
else:
    print('Authentication FAILED')
    
    # Check password hash
    print(f'Password hash: {user.password[:50]}...')
    print('Password might be incorrect')

# Test 3: Test authorization function
print('\n3. Testing authorization...')
can_login = is_admin_or_superadmin(user)
print(f'Can login (Admin/SuperAdmin): {can_login}')

# Test 4: Try different password combinations
print('\n4. Testing different passwords...')
passwords = ['TestPass123!', 'testpass123!', 'TestPass123', 'testpass123']
for pwd in passwords:
    auth_user = authenticate(username='TestSathvika', password=pwd)
    if auth_user:
        print(f'  SUCCESS with password: {pwd}')
        break
else:
    print('  No password worked - need to reset')

# Test 5: Reset password if needed
if auth_user is None:
    print('\n5. Resetting password...')
    user.set_password('TestPass123!')
    user.save()
    print('Password reset to TestPass123!')
    
    # Test again
    auth_user = authenticate(username='TestSathvika', password='TestPass123!')
    if auth_user:
        print('Authentication now works!')
    else:
        print('Still not working - deeper issue')

print('\n=== Manual Test Instructions ===')
print('1. Try these exact credentials:')
print('   Username: TestSathvika')
print('   Password: TestPass123!')
print('2. Make sure no extra spaces')
print('3. Check browser console (F12) for errors')
print('4. Try incognito/private window')
