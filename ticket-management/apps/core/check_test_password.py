#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

print('=== Check TestSathvika User Password ===')

try:
    # Find the admin user
    admin_user = User.objects.get(username='TestSathvika')
    print(f'User: {admin_user.username}')
    print(f'Email: {admin_user.email}')
    print(f'Created: {admin_user.date_joined}')
    print(f'Is Staff: {admin_user.is_staff}')
    print(f'Is Superuser: {admin_user.is_superuser}')
    
    # Check if password is set
    print(f'Has usable password: {admin_user.has_usable_password()}')
    
    # We can't see the actual password (it's hashed), but we can reset it
    print('\n=== Password Reset Options ===')
    print('1. Set a new password: python reset_test_password.py')
    print('2. Create a new test user: python create_new_test_user.py')
    
except User.DoesNotExist:
    print('TestSathvika user not found')
    print('Creating new test user...')
    
    # Create the user with a known password
    from users.models import UserProfile, Role
    
    user = User.objects.create_user(
        username='TestSathvika',
        email='sathvikatest@gmail.com',
        password='TestPass123!'  # Known password
    )
    user.is_staff = True
    user.save()
    
    # Assign Admin role
    role, _ = Role.objects.get_or_create(name='Admin')
    profile, created = UserProfile.objects.get_or_create(user=user)
    profile.role = role
    profile.save()
    
    print('✅ Created TestSathvika user')
    print('Username: TestSathvika')
    print('Password: TestPass123!')
    print('Email: sathvikatest@gmail.com')

except Exception as e:
    print(f'Error: {e}')
