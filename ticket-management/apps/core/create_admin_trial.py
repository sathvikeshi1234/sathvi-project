#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from superadmin.models import Company, Plan, Subscription
from django.utils import timezone

print('=== Create Trial Subscription for TestSathvika ===')

try:
    # Find the admin user
    admin_user = User.objects.get(username='TestSathvika')
    print(f'Found admin user: {admin_user.username}')
    
    # Create a company for the admin
    company, company_created = Company.objects.get_or_create(
        name=f'{admin_user.username} Company',
        defaults={
            'email': f'{admin_user.username}@company.com',
            'phone': '0000000000',
            'subscription_status': 'trial',
            'subscription_start_date': timezone.now().date(),
            'plan_expiry_date': timezone.now().date() + timezone.timedelta(days=30),
        }
    )
    
    print(f'Company {"created" if company_created else "found"}: {company.name}')
    print(f'Trial period: {company.subscription_start_date} to {company.plan_expiry_date}')
    
    # Get or create a plan
    plan = Plan.objects.filter(is_active=True).first()
    if not plan:
        plan = Plan.objects.create(
            name='Basic Plan',
            price=29.99,
            billing_cycle='monthly',
            users=10,
            storage='100GB',
            is_active=True
        )
        print(f'Created plan: {plan.name}')
    else:
        print(f'Found plan: {plan.name}')
    
    # Create trial subscription
    subscription, sub_created = Subscription.objects.get_or_create(
        company=company,
        defaults={
            'plan': plan,
            'status': 'trial',
            'start_date': timezone.now().date(),
            'end_date': timezone.now().date() + timezone.timedelta(days=30),
            'next_billing_date': timezone.now().date() + timezone.timedelta(days=30),
            'base_price': plan.price,
            'discount_amount': 0.00,
            'tax_amount': 0.00,
            'total_amount': plan.price,
            'auto_renew': True,
        }
    )
    
    if sub_created:
        print(f'✅ Trial subscription created successfully!')
        print(f'Subscription ID: {subscription.id}')
        print(f'Plan: {subscription.plan.name}')
        print(f'Status: {subscription.status}')
        print(f'Start date: {subscription.start_date}')
        print(f'End date: {subscription.end_date}')
        print(f'Days remaining: {(subscription.end_date - timezone.now().date()).days}')
        
        # Test if admin can access dashboard
        can_access = subscription.can_access_dashboard(admin_user)
        print(f'Can access dashboard: {can_access}')
        
        # Check trial status
        print(f'Trial active: {subscription.is_trial_active}')
        print(f'Payment required: {subscription.is_payment_required}')
        
    else:
        print(f'Subscription already exists: {subscription.id}')
        print(f'Status: {subscription.status}')
        print(f'End date: {subscription.end_date}')
        
        # Check if trial is still active
        days_remaining = (subscription.end_date - timezone.now().date()).days
        print(f'Days remaining: {days_remaining}')
        print(f'Trial active: {subscription.is_trial_active}')
        
except User.DoesNotExist:
    print('Admin user TestSathvika not found')
except Exception as e:
    print(f'Error: {e}')

print('\n=== Expiry Date Status ===')
today = timezone.now().date()
print(f'Today: {today}')

# Check all trial subscriptions
trial_subscriptions = Subscription.objects.filter(status='trial')
print(f'\nTotal trial subscriptions: {trial_subscriptions.count()}')

for sub in trial_subscriptions:
    days_remaining = (sub.end_date - today).days
    is_expired = days_remaining < 0
    
    print(f'\nSubscription {sub.id}:')
    print(f'  Company: {sub.company.name}')
    print(f'  Plan: {sub.plan.name}')
    print(f'  Status: {sub.status}')
    print(f'  End date: {sub.end_date}')
    print(f'  Days remaining: {days_remaining}')
    print(f'  Status: {"EXPIRED" if is_expired else "ACTIVE"}')
    print(f'  Trial active: {sub.is_trial_active}')
