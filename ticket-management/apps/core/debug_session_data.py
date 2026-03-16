#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from superadmin.views import check_subscription_expiry

print('=== Debug Session Data ===')

client = Client()

# Test 1: Check if user should see modal
admin_user = User.objects.get(username='TestSathvika')
should_show = check_subscription_expiry(admin_user)
print(f'Should show modal: {should_show}')

# Test 2: Simulate login process with session tracking
print('\n2. Testing login with session tracking...')

login_data = {
    'username': 'TestSathvika',
    'password': 'TestPass123!'
}

# Enable session tracking
client = Client(enforce_csrf_checks=False)

# Login
response = client.post('/superadmin/login/', data=login_data)
print(f'Login response: {response.status_code}')

# Check session data
print(f'Session data: {dict(client.session)}')
print(f'Session keys: {list(client.session.keys())}')

# Check if modal flag was set
if 'show_payment_modal' in client.session:
    print(f'Modal flag in session: {client.session["show_payment_modal"]}')
else:
    print('Modal flag NOT in session')

# Follow redirect to dashboard
if response.status_code == 302:
    dashboard_response = client.get(response.get('Location'))
    print(f'Dashboard response: {dashboard_response.status_code}')
    
    # Check session after dashboard
    print(f'Session after dashboard: {dict(client.session)}')
    
    # Check if modal flag was consumed (popped)
    if 'show_payment_modal' in client.session:
        print(f'Modal flag still in session: {client.session["show_payment_modal"]}')
    else:
        print('Modal flag consumed by dashboard view')

print('\n3. Testing direct dashboard access...')

# New client, login again
client2 = Client(enforce_csrf_checks=False)
client2.post('/superadmin/login/', data=login_data)

# Access dashboard directly
dashboard_response = client2.get('/superadmin/dashboard/')
print(f'Dashboard direct access: {dashboard_response.status_code}')

# Check response content for modal
content = dashboard_response.content.decode()
if 'paymentRequiredModal' in content:
    print('Modal HTML found in dashboard')
else:
    print('Modal HTML NOT found in dashboard')

# Check for any template includes
if 'payment_modal.html' in content:
    print('Modal template include found')
else:
    print('Modal template include NOT found')

print('\n=== Issue Analysis ===')
if should_show and 'show_payment_modal' not in client.session:
    print('PROBLEM: Session flag not being set during login')
elif should_show and 'paymentRequiredModal' not in content:
    print('PROBLEM: Modal not being included in template')
else:
    print('ISSUE: Something else - check browser console')
