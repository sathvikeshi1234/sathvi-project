#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from superadmin.models import Company, Plan, Subscription, Payment

print('=== Current Subscription Page Data Investigation ===')

# Check what data is currently being displayed
active_subscriptions = Subscription.objects.select_related('company', 'plan').filter(status='active').order_by('-created_at')
all_subscriptions = Subscription.objects.select_related('company', 'plan').order_by('-created_at')

print(f'Active subscriptions: {active_subscriptions.count()}')
print(f'Total subscriptions: {all_subscriptions.count()}')
print()

print('=== Active Subscriptions (currently displayed) ===')
for sub in active_subscriptions:
    print(f'ID: {sub.id} | Company: {sub.company.name} | Plan: {sub.plan.name} | Status: {sub.status} | Created: {sub.created_at}')

print('\n=== All Subscriptions ===')
for sub in all_subscriptions:
    print(f'ID: {sub.id} | Company: {sub.company.name} | Plan: {sub.plan.name} | Status: {sub.status} | Created: {sub.created_at}')

print('\n=== Companies and Their Plans ===')
companies = Company.objects.filter(is_active=True)
for company in companies:
    print(f'Company: {company.name}')
    print(f'  Plan: {company.plan.name if company.plan else "None"}')
    print(f'  Subscription Status: {company.subscription_status}')
    print(f'  Active Subscriptions: {company.subscriptions.filter(status="active").count()}')
    print()

print('=== Available Plans ===')
plans = Plan.objects.filter(is_active=True)
for plan in plans:
    print(f'Plan: {plan.name} | Price: ${plan.price} | Status: {plan.status} | Active: {plan.is_active}')
