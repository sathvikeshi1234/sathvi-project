#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import UserProfile, Role
from superadmin.models import Subscription, Company
from django.utils import timezone

print('=== Check Admin User Expiry Date ===')

# Find the admin user you created
try:
    admin_user = User.objects.get(username='TestSathvika')
    print(f'Found admin user: {admin_user.username}')
    print(f'Email: {admin_user.email}')
    print(f'Created: {admin_user.date_joined}')
    print(f'Is staff: {admin_user.is_staff}')
    
    # Check user profile and role
    try:
        profile = admin_user.userprofile
        role = profile.role.name if profile.role else 'No role'
        print(f'Role: {role}')
    except:
        print('No profile found')
    
    # Check if user has subscription
    print('\n=== Subscription Check ===')
    
    # Try to get user's company
    company = None
    try:
        # Check if user has a company relationship
        from superadmin.models import Company
        companies = Company.objects.all()
        print(f'Total companies in system: {companies.count()}')
        
        for comp in companies:
            print(f'Company: {comp.name} (ID: {comp.id})')
            # Check if this company has any relationship with the user
            # This depends on your company-user relationship model
            
    except Exception as e:
        print(f'Error checking companies: {e}')
    
    # Check subscriptions
    subscriptions = Subscription.objects.all()
    print(f'\nTotal subscriptions: {subscriptions.count()}')
    
    for sub in subscriptions:
        print(f'Subscription ID: {sub.id}')
        print(f'Company: {sub.company.name if sub.company else "No company"}')
        print(f'Plan: {sub.plan.name if sub.plan else "No plan"}')
        print(f'Status: {sub.status}')
        print(f'Start date: {sub.start_date}')
        print(f'End date: {sub.end_date}')
        print(f'Trial active: {sub.is_trial_active}')
        print(f'Payment required: {sub.is_payment_required}')
        print(f'Can access dashboard: {sub.can_access_dashboard(admin_user)}')
        print('---')
    
    # Check if admin user can access dashboard
    print('\n=== Dashboard Access Check ===')
    
    # Create a test subscription for this admin if none exists
    if subscriptions.count() == 0:
        print('No subscriptions found - creating test subscription for admin')
        
        try:
            # Create a test company
            company, created = Company.objects.get_or_create(
                name='Test Company',
                defaults={
                    'subscription_status': 'trial',
                    'trial_start_date': timezone.now().date(),
                    'trial_end_date': timezone.now().date() + timezone.timedelta(days=30),
                }
            )
            print(f'Company created: {created}')
            
            # Create a trial subscription
            from superadmin.models import Plan
            plan = Plan.objects.filter(is_active=True).first()
            if not plan:
                plan = Plan.objects.create(
                    name='Basic Plan',
                    price=Decimal('29.99'),
                    billing_cycle='monthly',
                    is_active=True
                )
            
            subscription = Subscription.objects.create(
                company=company,
                plan=plan,
                status='trial',
                start_date=timezone.now().date(),
                end_date=timezone.now().date() + timezone.timedelta(days=30),
            )
            
            print(f'Trial subscription created: {subscription.id}')
            print(f'Trial period: {subscription.start_date} to {subscription.end_date}')
            print(f'Trial active: {subscription.is_trial_active}')
            
        except Exception as e:
            print(f'Error creating test subscription: {e}')
    
except User.DoesNotExist:
    print('Admin user TestSathvika not found')
except Exception as e:
    print(f'Error: {e}')

print('\n=== Expiry Date Logic Test ===')
from datetime import datetime, timedelta

# Test trial expiry logic
print('Testing trial expiry calculations...')

# Create test dates
today = timezone.now().date()
trial_start = today
trial_end = today + timezone.timedelta(days=30)

print(f'Today: {today}')
print(f'Trial start: {trial_start}')
print(f'Trial end: {trial_end}')
print(f'Days until expiry: {(trial_end - today).days}')

# Test different scenarios
test_scenarios = [
    ('Active trial', today, today + timezone.timedelta(days=15)),
    ('Expiring soon', today, today + timezone.timedelta(days=2)),
    ('Expired', today, today - timezone.timedelta(days=5)),
    ('Starting today', today, today + timezone.timedelta(days=30)),
]

for scenario_name, start_date, end_date in test_scenarios:
    days_remaining = (end_date - today).days
    is_expired = end_date < today
    is_active = not is_expired and start_date <= today
    
    print(f'\n{scenario_name}:')
    print(f'  Start: {start_date}')
    print(f'  End: {end_date}')
    print(f'  Days remaining: {days_remaining}')
    print(f'  Is expired: {is_expired}')
    print(f'  Is active: {is_active}')
