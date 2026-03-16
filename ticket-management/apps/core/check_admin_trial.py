#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from superadmin.models import Subscription, Company
from django.utils import timezone

print('=== Check Admin User Subscription Status ===')

# Find the admin user
try:
    admin_user = User.objects.get(username='TestSathvika')
    print(f'Admin user: {admin_user.username}')
    print(f'Created: {admin_user.date_joined}')
    print(f'Is staff: {admin_user.is_staff}')
    
    # Check if admin has a personal subscription
    print('\n=== Personal Subscription Check ===')
    
    # Look for subscriptions that might be associated with this admin
    # Since your model links subscriptions to companies, we need to find
    # if this admin is associated with any company that has a subscription
    
    companies = Company.objects.all()
    admin_company = None
    
    for company in companies:
        # Check if this admin user is associated with this company
        # This depends on your company-user relationship model
        # Let's check if there's a way to associate this admin with a company
        
        # For now, let's see if we can find any subscription that could be for this admin
        print(f'Company: {company.name}')
        print(f'  Subscription status: {company.subscription_status}')
        print(f'  Trial start: {company.trial_start_date}')
        print(f'  Trial end: {company.trial_end_date}')
        
        # Check if this company has active subscription
        company_subs = Subscription.objects.filter(company=company)
        for sub in company_subs:
            print(f'  Subscription: {sub.plan.name if sub.plan else "No plan"}')
            print(f'    Status: {sub.status}')
            print(f'    Start: {sub.start_date}')
            print(f'    End: {sub.end_date}')
            print(f'    Can access: {sub.can_access_dashboard(admin_user)}')
        print('---')
    
    # The issue: Admin user needs a subscription or trial
    print('\n=== Issue Analysis ===')
    print('PROBLEM: Admin user TestSathvika has no subscription/trial')
    print('SOLUTION: Create a trial subscription for this admin user')
    
    # Create a trial subscription for the admin
    print('\n=== Creating Admin Trial Subscription ===')
    
    try:
        # Create a personal company for this admin or associate with existing
        company, created = Company.objects.get_or_create(
            name=f'{admin_user.username} Company',
            defaults={
                'subscription_status': 'trial',
                'trial_start_date': timezone.now().date(),
                'trial_end_date': timezone.now().date() + timezone.timedelta(days=30),
            }
        )
        print(f'Company {"created" if created else "found"}: {company.name}')
        
        # Get or create a plan for admin
        from superadmin.models import Plan
        plan = Plan.objects.filter(name='Admin Plan').first()
        if not plan:
            plan = Plan.objects.create(
                name='Admin Plan',
                price=29.99,
                billing_cycle='monthly',
                is_active=True
            )
        
        # Create trial subscription
        subscription, created = Subscription.objects.get_or_create(
            company=company,
            defaults={
                'plan': plan,
                'status': 'trial',
                'start_date': timezone.now().date(),
                'end_date': timezone.now().date() + timezone.timedelta(days=30),
            }
        )
        
        if created:
            print(f'Trial subscription created for admin!')
            print(f'Trial period: {subscription.start_date} to {subscription.end_date}')
            print(f'Days remaining: {(subscription.end_date - timezone.now().date()).days}')
            print(f'Trial active: {subscription.is_trial_active}')
            print(f'Can access dashboard: {subscription.can_access_dashboard(admin_user)}')
        else:
            print(f'Subscription already exists: {subscription.id}')
            print(f'Status: {subscription.status}')
            
    except Exception as e:
        print(f'Error creating subscription: {e}')
    
except User.DoesNotExist:
    print('Admin user not found')
except Exception as e:
    print(f'Error: {e}')

print('\n=== Trial Expiry Test ===')
from datetime import datetime, timedelta

today = timezone.now().date()
print(f'Today: {today}')

# Test the trial expiry logic
trial_end = today + timezone.timedelta(days=30)
print(f'Trial end date: {trial_end}')
print(f'Days until expiry: {(trial_end - today).days}')

# Check if trial is active
is_trial_active = today <= trial_end
print(f'Trial is active: {is_trial_active}')

# Test expiry scenarios
print('\n=== Expiry Scenarios ===')
scenarios = [
    ('Today', today),
    ('Tomorrow', today + timezone.timedelta(days=1)),
    ('15 days', today + timezone.timedelta(days=15)),
    ('29 days', today + timezone.timedelta(days=29)),
    ('30 days', today + timezone.timedelta(days=30)),
    ('31 days (expired)', today + timezone.timedelta(days=31)),
]

for name, test_date in scenarios:
    days_remaining = (test_date - today).days
    is_expired = test_date < today
    print(f'{name}: {test_date} - {"EXPIRED" if is_expired else f"{days_remaining} days remaining"}')
