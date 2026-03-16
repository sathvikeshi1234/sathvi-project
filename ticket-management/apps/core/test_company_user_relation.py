#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from superadmin.models import Company
from users.models import UserProfile, Role

print('=== Testing Company-User Relationship ===')

# Check if Company model has user relationship
company = Company.objects.first()
if company:
    print(f'Testing with company: {company.name}')
    
    # Try to access users
    try:
        users = company.user_set.all()
        print(f'Company has {users.count()} users')
        for user in users:
            try:
                profile = user.userprofile
                print(f'  - {user.username} ({profile.role.name if profile.role else "No role"})')
            except:
                print(f'  - {user.username} (No profile)')
    except AttributeError as e:
        print(f'Company does not have user_set relationship: {e}')
        
        # Alternative: Check UserProfile directly
        print('\nTrying alternative approach...')
        admin_role = Role.objects.filter(name__in=['Admin', 'SuperAdmin'])
        if admin_role.exists():
            admin_profiles = UserProfile.objects.filter(role__in=admin_role)
            print(f'Found {admin_profiles.count()} admin/superadmin profiles')
            
            # We need to modify the approach since Company-User relationship isn't clear
            print('\nNeed to create a different approach for role-based trial access')

else:
    print('No company found')
