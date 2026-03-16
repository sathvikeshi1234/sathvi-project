#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

print('=== DEBUG REGULAR USER LOGIN ===')

# Test 1: Check if regular users exist
print('1. Checking for regular company users...')
from django.contrib.auth.models import User
from users.models import UserProfile, Role

regular_users = User.objects.filter(
    userprofile__role__name='Customer'
).exclude(username='TestSathvika')

print(f'Found {regular_users.count()} regular users')
for user in regular_users[:3]:
    print(f'  - {user.username} ({user.email})')

if regular_users.count() == 0:
    print('No regular users found - creating test user...')
    # Create a test regular user
    test_user = User.objects.create_user(
        username='TestCustomer',
        email='customer@test.com',
        password='CustomerPass123!'
    )
    
    # Assign Customer role
    customer_role = Role.objects.get_or_create(name='Customer')[0]
    profile = UserProfile.objects.get_or_create(user=test_user)[0]
    profile.role = customer_role
    profile.save()
    
    print('Created test user:')
    print('  Username: TestCustomer')
    print('  Password: CustomerPass123!')
    print('  Role: Customer')

# Test 2: Test regular user login
print('\n2. Testing regular user login...')
from django.contrib.auth import authenticate
from django.test import Client

test_user = User.objects.get(username='TestCustomer')
print(f'Testing user: {test_user.username}')

# Test authentication
auth_result = authenticate(username='TestCustomer', password='CustomerPass123!')
if auth_result:
    print('Authentication: SUCCESS')
else:
    print('Authentication: FAILED')

# Test login view
client = Client()
login_data = {
    'username': 'TestCustomer',
    'password': 'CustomerPass123!'
}

# Test main login endpoint
response = client.post('/login/', data=login_data)
print(f'Main login (/login/) status: {response.status_code}')

if response.status_code == 302:
    print('Main login: SUCCESS - redirecting')
    redirect_url = response.get('Location')
    print(f'Redirecting to: {redirect_url}')
elif response.status_code == 200:
    print('Main login: FAILED - showing login form again')
    content = response.content.decode()
    if 'Invalid' in content:
        print('Error message found in response')
    else:
        print('No error message visible')

# Test user-specific login endpoint
response = client.post('/user-login/', data=login_data)
print(f'User login (/user-login/) status: {response.status_code}')

if response.status_code == 302:
    print('User login: SUCCESS - redirecting')
    redirect_url = response.get('Location')
    print(f'Redirecting to: {redirect_url}')
elif response.status_code == 200:
    print('User login: FAILED - showing login form again')

print('\n3. URL Routing Check...')
from django.urls import reverse

try:
    main_login_url = reverse('login')
    print(f'Main login URL: {main_login_url}')
except:
    print('Main login URL not found')

try:
    user_login_url = reverse('user_login')
    print(f'User login URL: {user_login_url}')
except:
    print('User login URL not found')

print('\n4. Test Instructions for Regular Users:')
print('Regular users should use:')
print('URL: http://127.0.0.1:8000/login/')
print('Username: TestCustomer')
print('Password: CustomerPass123!')

print('\nIf regular users are using wrong URL:')
print('- They might be going to /superadmin/login/ (for admins only)')
print('- They should use /login/ (for regular users)')

print('\n=== SOLUTION ===')
print('1. Regular users: http://127.0.0.1:8000/login/')
print('2. Admin users: http://127.0.0.1:8000/superadmin/login/')
print('3. Test with created user: TestCustomer / CustomerPass123!')
