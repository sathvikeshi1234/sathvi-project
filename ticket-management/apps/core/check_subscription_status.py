#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from superadmin.models import Company, Subscription

print('=== Subscription Status Check ===')
print(f'Companies: {Company.objects.all().count()}')
print(f'Subscriptions: {Subscription.objects.all().count()}')
print()

companies = Company.objects.all()
for company in companies:
    print(f'Company: {company.name}')
    print(f'  Plan: {company.plan.name if company.plan else "None"}')
    print(f'  Subscription Status: {company.subscription_status}')
    print(f'  Plan Expiry: {company.plan_expiry_date}')
    print(f'  Subscriptions Count: {company.subscriptions.count()}')
    
    # Check active subscriptions
    active_subs = company.subscriptions.filter(status='active')
    if active_subs.exists():
        print(f'  Active Subscriptions: {active_subs.count()}')
        for sub in active_subs:
            print(f'    - Plan: {sub.plan.name}, Status: {sub.status}, Start: {sub.start_date}, End: {sub.end_date}')
    else:
        print('  No active subscriptions found')
    print()
