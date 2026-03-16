#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import UserProfile, Role

print('=== Database User Analysis ===')

# Analyze the user data you showed
email = 'sathvi589@gmail.com'
username = 'sathvi'

try:
    user = User.objects.get(email=email)
    print(f'Found user: {user.username}')
    print(f'Email: {user.email}')
    print(f'First name: {user.first_name}')
    print(f'Last name: {user.last_name}')
    print(f'Is active: {user.is_active}')
    print(f'Is staff: {user.is_staff}')
    print(f'Is superuser: {user.is_superuser}')
    print(f'Date joined: {user.date_joined}')
    print(f'Last login: {user.last_login}')
    
    # Check user profile
    try:
        profile = user.userprofile
        print(f'\nUser Profile:')
        print(f'Role: {profile.role.name if profile.role else "No role"}')
        print(f'Phone: {profile.phone}')
        print(f'City: {profile.city}')
        print(f'Is active: {profile.is_active}')
        
        # Check trial access based on role
        if profile.role and profile.role.name in ['Admin', 'SuperAdmin']:
            print(f'This user can access 30-day free trial')
        else:
            print(f'This user cannot access trial (role: {profile.role.name if profile.role else "None"})')
            
    except UserProfile.DoesNotExist:
        print('No user profile found')
    
    # Check company association
    from superadmin.models import Company, Subscription
    
    companies = Company.objects.all()
    print(f'\nAvailable companies: {companies.count()}')
    for company in companies:
        print(f'- {company.name}')
    
    # Check if user has any subscription access
    print(f'\nSubscription Access Check:')
    if companies.exists():
        company = companies.first()
        subscriptions = Subscription.objects.filter(company=company)
        print(f'Company: {company.name}')
        print(f'Subscriptions: {subscriptions.count()}')
        
        for sub in subscriptions:
            print(f'- {sub.plan.name} ({sub.status})')
            if sub.status == 'trial':
                can_access = sub.can_access_dashboard(user=user)
                print(f'  Trial access for {user.username}: {can_access}')
            elif sub.status == 'active':
                print(f'  Active access for {user.username}: True')
                
except User.DoesNotExist:
    print(f'User with email {email} not found')

print('\n=== Password Hash Analysis ===')
print('The password hash you showed: pbkdf2_sha256$600000$XY6UX7hOl4r6sd1h9UVp7g$PlMFQz5BEJFPSJA8vp1d/+i4NEk0FTha1DFuvVKpic8=')
print('- Algorithm: PBKDF2-SHA256')
print('- Iterations: 600,000 (secure)')
print('- This is Django\'s default secure password hashing')
print('- Password is properly encrypted and stored securely')
