#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from superadmin.models import Company, Plan, Subscription, Payment
from datetime import date, timedelta

print('=== Implementing 30-Day Free Trial System ===')

# Create a trial subscription for testing
company = Company.objects.first()
plan = Plan.objects.filter(name='Basic').first()

if company and plan:
    print(f'Testing with company: {company.name}')
    print(f'Testing with plan: {plan.name}')
    
    # Create a trial subscription
    trial_start = date.today() - timedelta(days=15)  # 15 days ago (still in trial)
    
    # Deactivate existing subscriptions first
    Subscription.objects.filter(company=company).update(status='cancelled')
    
    trial_subscription = Subscription.objects.create(
        company=company,
        plan=plan,
        status='trial',
        billing_cycle='monthly',
        start_date=trial_start,
        end_date=trial_start + timedelta(days=30),  # Trial ends after 30 days
        next_billing_date=trial_start + timedelta(days=30),
        base_price=plan.price,
        total_amount=plan.price
    )
    
    print(f'Created trial subscription: {trial_subscription.id}')
    print(f'Trial start: {trial_subscription.start_date}')
    print(f'Trial end: {trial_subscription.end_date}')
    
    # Test trial properties
    print(f'\n=== Trial Status Check ===')
    print(f'Is trial active: {trial_subscription.is_trial_active}')
    print(f'Trial days remaining: {trial_subscription.trial_days_remaining}')
    print(f'Is payment required: {trial_subscription.is_payment_required}')
    print(f'Can access dashboard: {trial_subscription.can_access_dashboard}')
    
    # Test expired trial
    print(f'\n=== Testing Expired Trial ===')
    expired_start = date.today() - timedelta(days=35)  # 35 days ago (expired)
    
    expired_trial = Subscription.objects.create(
        company=company,
        plan=plan,
        status='trial',
        billing_cycle='monthly',
        start_date=expired_start,
        end_date=expired_start + timedelta(days=30),
        next_billing_date=expired_start + timedelta(days=30),
        base_price=plan.price,
        total_amount=plan.price
    )
    
    print(f'Expired trial start: {expired_trial.start_date}')
    print(f'Expired trial end: {expired_trial.end_date}')
    print(f'Is trial active: {expired_trial.is_trial_active}')
    print(f'Trial days remaining: {expired_trial.trial_days_remaining}')
    print(f'Is payment required: {expired_trial.is_payment_required}')
    print(f'Can access dashboard: {expired_trial.can_access_dashboard}')
    
    # Test payment activation
    print(f'\n=== Testing Payment Activation ===')
    print(f'Before payment - Status: {expired_trial.status}')
    print(f'Before payment - Can access: {expired_trial.can_access_dashboard}')
    
    expired_trial.activate_subscription_after_payment()
    
    print(f'After payment - Status: {expired_trial.status}')
    print(f'After payment - Can access: {expired_trial.can_access_dashboard}')
    
    # Clean up test subscriptions
    Subscription.objects.filter(company=company, status__in=['trial', 'cancelled']).delete()
    print(f'\nCleaned up test subscriptions')

else:
    print('No company or plan found for testing')
