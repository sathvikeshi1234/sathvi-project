#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

print('=== Reset TestSathvika Password ===')

try:
    # Find the admin user
    admin_user = User.objects.get(username='TestSathvika')
    
    # Set a new password
    new_password = 'TestPass123!'
    admin_user.set_password(new_password)
    admin_user.save()
    
    print(f'✅ Password reset successfully!')
    print(f'Username: {admin_user.username}')
    print(f'New Password: {new_password}')
    print(f'Email: {admin_user.email}')
    
    print(f'\n=== Login Credentials ===')
    print(f'URL: http://127.0.0.1:8000/superadmin/login/')
    print(f'Username: TestSathvika')
    print(f'Password: {new_password}')
    
    print(f'\n=== Test Instructions ===')
    print('1. Go to login page')
    print('2. Enter credentials above')
    print('3. Payment modal should appear (trial is expired)')
    print('4. Test plan selection and payment flow')
    
except User.DoesNotExist:
    print('TestSathvika user not found')
except Exception as e:
    print(f'Error: {e}')
