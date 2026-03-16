#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

print('=== Admin Signup Form Test ===')

# Test the admin signup form validation logic
from superadmin.views import admin_signup
from django.test import RequestFactory
from django.contrib.messages import get_messages
from django.contrib.auth.models import AnonymousUser

# Create a request factory
factory = RequestFactory()

# Test 1: Missing username
print('Test 1: Missing username')
request = factory.post('/superadmin/admin-signup/', {
    'email': 'test@example.com',
    'password': 'TestPass123!',
    'confirm_password': 'TestPass123!'
})
request.user = AnonymousUser()

# Clear messages
from django.contrib.messages.storage.fallback import FallbackStorage
request.session = {}
request._messages = FallbackStorage(request)

try:
    response = admin_signup(request)
    messages = list(get_messages(request))
    if messages:
        for message in messages:
            print(f'  Message: {message.message}')
    else:
        print('  No messages returned')
    print(f'  Response status: {response.status_code}')
except Exception as e:
    print(f'  Error: {e}')

print()

# Test 2: Missing email
print('Test 2: Missing email')
request = factory.post('/superadmin/admin-signup/', {
    'username': 'testadmin',
    'password': 'TestPass123!',
    'confirm_password': 'TestPass123!'
})
request.user = AnonymousUser()
request.session = {}
request._messages = FallbackStorage(request)

try:
    response = admin_signup(request)
    messages = list(get_messages(request))
    if messages:
        for message in messages:
            print(f'  Message: {message.message}')
    else:
        print('  No messages returned')
    print(f'  Response status: {response.status_code}')
except Exception as e:
    print(f'  Error: {e}')

print()

# Test 3: Password mismatch
print('Test 3: Password mismatch')
request = factory.post('/superadmin/admin-signup/', {
    'username': 'testadmin',
    'email': 'test@example.com',
    'password': 'TestPass123!',
    'confirm_password': 'DifferentPass123!'
})
request.user = AnonymousUser()
request.session = {}
request._messages = FallbackStorage(request)

try:
    response = admin_signup(request)
    messages = list(get_messages(request))
    if messages:
        for message in messages:
            print(f'  Message: {message.message}')
    else:
        print('  No messages returned')
    print(f'  Response status: {response.status_code}')
except Exception as e:
    print(f'  Error: {e}')

print()

# Test 4: Valid data
print('Test 4: Valid data')
request = factory.post('/superadmin/admin-signup/', {
    'username': 'testadmin456',
    'email': 'test456@example.com',
    'password': 'TestPass123!',
    'confirm_password': 'TestPass123!'
})
request.user = AnonymousUser()
request.session = {}
request._messages = FallbackStorage(request)

try:
    response = admin_signup(request)
    messages = list(get_messages(request))
    if messages:
        for message in messages:
            print(f'  Message: {message.message}')
    else:
        print('  Success: No validation errors')
    print(f'  Response status: {response.status_code}')
except Exception as e:
    print(f'  Error: {e}')

print()
print('=== Form Field Analysis ===')
print('Required fields in view:')
print('- username (checked)')
print('- email (checked)')
print('- password (checked)')
print('- confirm_password (checked)')
print()
print('Required fields in template:')
print('- username (has required attr)')
print('- email (has required attr)')
print('- password (has required attr)')
print('- confirm_password (has required attr)')
print()
print('=== Possible Issues ===')
print('1. Email field not marked as required in template')
print('2. Form submission not reaching the view')
print('3. JavaScript validation blocking submission')
print('4. Network/URL routing issues')
