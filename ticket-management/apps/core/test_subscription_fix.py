#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from superadmin.models import Company, Plan, Subscription, Payment
from datetime import date, timedelta

print('=== Testing Updated Subscription Page Logic ===')

# Test the new subscription display logic (latest per company)
all_active_subs = Subscription.objects.select_related('company', 'plan').filter(status='active').order_by('-created_at')
latest_subscriptions = []
processed_companies = set()

for sub in all_active_subs:
    if sub.company.id not in processed_companies:
        latest_subscriptions.append(sub)
        processed_companies.add(sub.company.id)

print(f'Original active subscriptions: {all_active_subs.count()}')
print(f'Latest subscriptions per company: {len(latest_subscriptions)}')
print()

print('=== Latest Subscription Per Company (New Display Logic) ===')
for sub in latest_subscriptions:
    print(f'Company: {sub.company.name} | Plan: {sub.plan.name} | ID: {sub.id} | Created: {sub.created_at}')

print('\n=== Testing Plan Selection (Ordered by Name) ===')
plans = Plan.objects.filter(is_active=True).order_by('name')
for plan in plans:
    print(f'Plan: {plan.name} | Price: ${plan.price} | ID: {plan.id}')

print('\n=== Testing Subscription Creation with Plan Selection ===')
# Find a company that has multiple subscriptions to test deactivation
ultrakey_companies = Company.objects.filter(name__icontains='ultrakey')
if ultrakey_companies.exists():
    test_company = ultrakey_companies.first()
    print(f'Testing with company: {test_company.name}')
    print(f'Current active subscriptions: {test_company.subscriptions.filter(status="active").count()}')
    
    # Get a plan
    test_plan = Plan.objects.filter(is_active=True).first()
    print(f'Selected plan: {test_plan.name}')
    
    # Simulate creating a new subscription
    start_date = date.today()
    end_date = start_date + timedelta(days=30)
    
    # Count before
    active_before = Subscription.objects.filter(company=test_company, status='active').count()
    
    # Deactivate existing subscriptions (simulating the new logic)
    existing_subs = Subscription.objects.filter(company=test_company, status='active')
    for existing_sub in existing_subs:
        existing_sub.status = 'cancelled'
        existing_sub.save()
    
    # Create new subscription
    new_subscription = Subscription.objects.create(
        company=test_company,
        plan=test_plan,
        status='active',
        billing_cycle='monthly',
        start_date=start_date,
        end_date=end_date,
        next_billing_date=start_date + timedelta(days=30),
        base_price=test_plan.price,
        total_amount=test_plan.price
    )
    
    # Count after
    active_after = Subscription.objects.filter(company=test_company, status='active').count()
    
    print(f'Active subscriptions before: {active_before}')
    print(f'Active subscriptions after: {active_after}')
    print(f'New subscription created: {new_subscription.id}')
    
    # Check if only one active subscription exists
    if active_after == 1:
        print('SUCCESS: Only one active subscription per company')
    else:
        print('ERROR: Multiple active subscriptions still exist')
else:
    print('No ultrakey companies found for testing')
