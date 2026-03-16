#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

print('=== CHECKING WHATS AT /admin-signup/ ===')

from django.test import Client
client = Client()

# Check what's at the URL you're using
response = client.get('/admin-signup/')
print(f'Status: {response.status_code}')

if response.status_code == 200:
    content = response.content.decode()
    
    # Check what type of page this is
    if 'Create Admin Account' in content:
        print('This is an admin signup form')
    elif 'Super Admin' in content:
        print('This is a super admin signup form')
    elif 'Ticket Management System' in content:
        print('This appears to be the main landing page')
    else:
        print('Unknown page type')
    
    # Show form action
    if 'action=' in content:
        import re
        action_match = re.search(r'action="([^"]*)"', content)
        if action_match:
            form_action = action_match.group(1)
            print(f'Form action: {form_action}')
    
    # Check if it's the users app admin signup
    if 'users' in content.lower() or 'customer' in content.lower():
        print('This might be the users app admin signup (different functionality)')

print('\n=== URL COMPARISON ===')
print('You are using:     /admin-signup/     (users app - different functionality)')
print('You should use:    /superadmin/admin-signup/  (superadmin app - correct one)')

print('\n=== DIFFERENCE ===')
print('/admin-signup/ (users app):')
print('- Creates admin users for regular users system')
print('- May not create trial subscriptions')
print('- May not integrate with payment system')

print('\n/superadmin/admin-signup/ (superadmin app):')
print('- Creates admin users with trial subscriptions')
print('- Integrates with payment modal system')
print('- Creates company and subscription automatically')

print('\n=== SOLUTION ===')
print('Use this URL for admin signup:')
print('http://127.0.0.1:8000/superadmin/admin-signup/')
