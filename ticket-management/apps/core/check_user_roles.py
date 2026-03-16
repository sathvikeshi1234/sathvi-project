#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import Role, UserProfile
from django.contrib.auth.models import User

print('=== User Role Analysis ===')

# Check all roles
roles = Role.objects.all()
print(f'Total roles: {roles.count()}')
for role in roles:
    print(f'Role: {role.name}')

print('\n=== User Profiles by Role ===')

# Check users by role
for role in roles:
    users_with_role = UserProfile.objects.filter(role=role)
    print(f'{role.name}: {users_with_role.count()} users')
    for profile in users_with_role:
        print(f'  - {profile.user.username} ({profile.user.email})')

print('\n=== Admin vs Agent vs User Analysis ===')

admin_role = Role.objects.filter(name='Admin').first()
agent_role = Role.objects.filter(name='Agent').first()
user_role = Role.objects.filter(name='User').first()
superadmin_role = Role.objects.filter(name='SuperAdmin').first()

print(f'Admin role exists: {admin_role is not None}')
print(f'Agent role exists: {agent_role is not None}')
print(f'User role exists: {user_role is not None}')
print(f'SuperAdmin role exists: {superadmin_role is not None}')

if admin_role:
    admin_users = UserProfile.objects.filter(role=admin_role)
    print(f'\nAdmin users ({admin_users.count()}):')
    for profile in admin_users:
        print(f'  - {profile.user.username}')

if agent_role:
    agent_users = UserProfile.objects.filter(role=agent_role)
    print(f'\nAgent users ({agent_users.count()}):')
    for profile in agent_users:
        print(f'  - {profile.user.username}')

if user_role:
    regular_users = UserProfile.objects.filter(role=user_role)
    print(f'\nRegular users ({regular_users.count()}):')
    for profile in regular_users:
        print(f'  - {profile.user.username}')
