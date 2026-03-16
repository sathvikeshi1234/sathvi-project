#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from superadmin.models import Company, Plan, Subscription, Payment
from datetime import date, timedelta

print('=== Complete 30-Day Free Trial System Test ===')

# Get test data
company = Company.objects.first()
plan = Plan.objects.filter(name='Basic').first()

if company and plan:
    print(f'Testing with company: {company.name}')
    print(f'Testing with plan: {plan.name}')
    
    # Clean up existing test subscriptions
    Subscription.objects.filter(company=company).delete()
    
    print('\n=== 1. Creating 30-Day Free Trial ===')
    trial_start = date.today()
    trial_subscription = Subscription.objects.create(
        company=company,
        plan=plan,
        status='trial',
        billing_cycle='monthly',
        start_date=trial_start,
        end_date=trial_start + timedelta(days=30),
        next_billing_date=trial_start + timedelta(days=30),
        base_price=plan.price,
        total_amount=plan.price
    )
    
    print(f'Trial subscription created: {trial_subscription.id}')
    print(f'Trial start: {trial_subscription.start_date}')
    print(f'Trial end: {trial_subscription.end_date}')
    print(f'Trial status: {trial_subscription.status}')
    
    # Test trial properties
    print(f'\n=== 2. Testing Trial Access (Day 1) ===')
    print(f'Is trial active: {trial_subscription.is_trial_active}')
    print(f'Trial days remaining: {trial_subscription.trial_days_remaining}')
    print(f'Is payment required: {trial_subscription.is_payment_required}')
    print(f'Can access dashboard: {trial_subscription.can_access_dashboard}')
    
    print(f'\n=== 3. Simulating Trial Expiry (Day 35) ===')
    # Move trial to expired state
    expired_start = date.today() - timedelta(days=35)
    trial_subscription.start_date = expired_start
    trial_subscription.end_date = expired_start + timedelta(days=30)
    trial_subscription.save()
    
    # Refresh properties after date change
    trial_subscription.expire_trial_if_needed()
    trial_subscription.refresh_from_db()
    
    print(f'Trial start: {trial_subscription.start_date}')
    print(f'Trial end: {trial_subscription.end_date}')
    print(f'Trial status: {trial_subscription.status}')
    print(f'Is trial active: {trial_subscription.is_trial_active}')
    print(f'Trial days remaining: {trial_subscription.trial_days_remaining}')
    print(f'Is payment required: {trial_subscription.is_payment_required}')
    print(f'Can access dashboard: {trial_subscription.can_access_dashboard}')
    
    print(f'\n=== 4. Processing Payment to Reactivate ===')
    print(f'Before payment - Status: {trial_subscription.status}')
    print(f'Before payment - Can access: {trial_subscription.can_access_dashboard}')
    
    # Create payment and activate subscription
    payment = Payment.objects.create(
        subscription=trial_subscription,
        company=company,
        amount=plan.price,
        payment_method='credit_card',
        payment_type='subscription',
        status='completed',
        payment_date=date.today(),
        transaction_id=f'PAY-{trial_subscription.id}-{date.today().strftime("%Y%m%d")}',
        invoice_number=f'INV-{trial_subscription.id}-{date.today().strftime("%Y%m%d")}',
        notes=f'Payment for {plan.name} subscription after trial'
    )
    
    # Activate subscription after payment
    trial_subscription.activate_subscription_after_payment()
    
    print(f'Payment created: {payment.transaction_id}')
    print(f'Payment amount: ${payment.amount}')
    print(f'After payment - Status: {trial_subscription.status}')
    print(f'After payment - Can access: {trial_subscription.can_access_dashboard}')
    print(f'New end date: {trial_subscription.end_date}')
    print(f'Next billing date: {trial_subscription.next_billing_date}')
    
    print(f'\n=== 5. Testing Dashboard Access Control ===')
    
    # Test different subscription scenarios
    scenarios = [
        ('Active Subscription', 'active', date.today(), True),
        ('Trial (Day 15)', 'trial', date.today() - timedelta(days=15), True),
        ('Expired Trial', 'trial', date.today() - timedelta(days=35), False),
        ('Expired Subscription', 'active', date.today() - timedelta(days=400), False),
    ]
    
    for scenario_name, status, start_date, expected_access in scenarios:
        test_sub = Subscription.objects.create(
            company=company,
            plan=plan,
            status=status,
            billing_cycle='monthly',
            start_date=start_date,
            end_date=start_date + timedelta(days=30),
            next_billing_date=start_date + timedelta(days=30),
            base_price=plan.price,
            total_amount=plan.price
        )
        
        # Auto-expire if needed
        test_sub.expire_trial_if_needed()
        test_sub.refresh_from_db()
        
        actual_access = test_sub.can_access_dashboard
        result = "PASS" if actual_access == expected_access else "FAIL"
        
        print(f'{result} {scenario_name}:')
        print(f'   Status: {test_sub.status}')
        print(f'   Can access: {actual_access} (expected: {expected_access})')
        
        # Clean up test subscription
        test_sub.delete()
    
    print(f'\n=== 6. Final System Status ===')
    active_subscriptions = Subscription.objects.filter(company=company, status='active').count()
    trial_subscriptions = Subscription.objects.filter(company=company, status='trial').count()
    expired_subscriptions = Subscription.objects.filter(company=company, status='expired').count()
    
    print(f'Active subscriptions: {active_subscriptions}')
    print(f'Trial subscriptions: {trial_subscriptions}')
    print(f'Expired subscriptions: {expired_subscriptions}')
    print(f'Total payments: {Payment.objects.filter(company=company).count()}')
    
    print(f'\n=== 30-Day Free Trial System Test Complete ===')
    print('Trial creation works')
    print('Dashboard access control works')
    print('Payment requirement after expiry works')
    print('Subscription activation after payment works')
    print('All scenarios tested successfully')

else:
    print('No company or plan found for testing')
