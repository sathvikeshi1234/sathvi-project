#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from superadmin.views import is_admin_or_superadmin

print('=== Test Admin Login Fix ===')

try:
    # Find the admin user
    admin_user = User.objects.get(username='TestSathvika')
    print(f'User: {admin_user.username}')
    print(f'Role: Admin')
    
    # Test the new function
    can_login = is_admin_or_superadmin(admin_user)
    print(f'Can login with new function: {can_login}')
    
    if can_login:
        print('SUCCESS: Admin user can now login!')
        print('\n=== Login Credentials ===')
        print('URL: http://127.0.0.1:8000/superadmin/login/')
        print('Username: TestSathvika')
        print('Password: TestPass123!')
        print('\nPayment modal should appear after login!')
    else:
        print('ISSUE: Still cannot login')
        
except Exception as e:
    print(f'Error: {e}')
