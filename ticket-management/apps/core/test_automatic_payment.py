#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from superadmin.models import Company, Plan, Subscription, Payment
from datetime import date, timedelta

print('=== Testing Automatic Payment Creation ===')

# Find a company and plan for testing
company = Company.objects.first()
plan = Plan.objects.first()

if company and plan:
    print(f'Testing with company: {company.name}')
    print(f'Testing with plan: {plan.name}')
    
    # Count before
    subscriptions_before = Subscription.objects.count()
    payments_before = Payment.objects.count()
    
    print(f'Subscriptions before: {subscriptions_before}')
    print(f'Payments before: {payments_before}')
    
    # Create a new subscription
    start_date = date.today()
    end_date = start_date + timedelta(days=30)
    
    subscription = Subscription.objects.create(
        company=company,
        plan=plan,
        status='active',
        billing_cycle='monthly',
        start_date=start_date,
        end_date=end_date,
        next_billing_date=start_date + timedelta(days=30),
        base_price=plan.price,
        total_amount=plan.price
    )
    
    print(f'Created subscription: {subscription.id}')
    
    # Count after
    subscriptions_after = Subscription.objects.count()
    payments_after = Payment.objects.count()
    
    print(f'Subscriptions after: {subscriptions_after}')
    print(f'Payments after: {payments_after}')
    
    # Check if payment was created
    new_payment = Payment.objects.filter(subscription=subscription).first()
    if new_payment:
        print(f'SUCCESS: Automatic payment created: {new_payment}')
        print(f'   Amount: ${new_payment.amount}')
        print(f'   Status: {new_payment.status}')
        print(f'   Transaction ID: {new_payment.transaction_id}')
        print(f'   Payment Date: {new_payment.payment_date}')
    else:
        print('ERROR: No automatic payment created')
    
    # Test with inactive subscription
    print('\n=== Testing Inactive Subscription (should not create payment) ===')
    payments_before_inactive = Payment.objects.count()
    
    inactive_subscription = Subscription.objects.create(
        company=company,
        plan=plan,
        status='trial',  # Not active
        billing_cycle='monthly',
        start_date=start_date,
        end_date=end_date,
        next_billing_date=start_date + timedelta(days=30),
        base_price=plan.price,
        total_amount=plan.price
    )
    
    payments_after_inactive = Payment.objects.count()
    
    if payments_after_inactive == payments_before_inactive:
        print('SUCCESS: Correctly no payment created for inactive subscription')
    else:
        print('ERROR: Payment incorrectly created for inactive subscription')

else:
    print('No company or plan found for testing')
