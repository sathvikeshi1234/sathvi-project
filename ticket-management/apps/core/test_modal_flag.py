#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

print('=== Test Modal Flag Setting ===')

client = Client()

# Login and check if modal flag is set
login_data = {
    'username': 'TestSathvika',
    'password': 'TestPass123!'
}

print('1. Logging in...')
response = client.post('/superadmin/login/', data=login_data, follow=False)
print(f'Login status: {response.status_code}')

if response.status_code == 302:
    # Follow redirect to dashboard
    dashboard_response = client.get(response.get('Location'))
    print(f'Dashboard status: {dashboard_response.status_code}')
    
    # Check if modal data is in the context
    if hasattr(dashboard_response, 'context') and dashboard_response.context:
        context = dashboard_response.context
        print(f'Show payment modal: {context.get("show_payment_modal", False)}')
        print(f'Plan name: {context.get("plan_name", "None")}')
        print(f'Expiry date: {context.get("expiry_date", "None")}')
        print(f'Days expired: {context.get("days_expired", 0)}')
    else:
        print('No context available (template response)')
        print(f'Response type: {type(dashboard_response)}')
    
    # Check response content for modal
    content = dashboard_response.content.decode()
    if 'paymentRequiredModal' in content:
        print('Modal HTML found in response')
    else:
        print('Modal HTML NOT found in response')
    
    if 'show_payment_modal' in content:
        print('Modal flag found in content')
    else:
        print('Modal flag NOT found in content')

print('\n=== Manual Test Instructions ===')
print('1. Open browser: http://127.0.0.1:8000/superadmin/login/')
print('2. Login: TestSathvika / TestPass123!')
print('3. Open Developer Tools (F12)')
print('4. Check Console tab for JavaScript errors')
print('5. Check Network tab for failed requests')
print('6. Look for modal in page source (Ctrl+U)')

print('\n=== If Modal Not Showing ===')
print('Possible issues:')
print('1. JavaScript errors preventing modal initialization')
print('2. Bootstrap not loaded properly')
print('3. Modal CSS conflicts')
print('4. Session data not being passed correctly')
