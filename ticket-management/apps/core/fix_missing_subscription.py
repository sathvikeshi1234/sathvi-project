#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from superadmin.models import Company, Subscription
from datetime import date, timedelta

print('=== Creating Missing Subscription for Tech Mahindra ===')

# Find tech mahindra company
tech_mahindra = Company.objects.filter(name__icontains='tech mahindra').first()
if tech_mahindra:
    print(f'Found company: {tech_mahindra.name}')
    print(f'Current plan: {tech_mahindra.plan.name if tech_mahindra.plan else "None"}')
    print(f'Subscription status: {tech_mahindra.subscription_status}')
    print(f'Current subscriptions: {tech_mahindra.subscriptions.count()}')
    
    if tech_mahindra.plan and tech_mahindra.subscriptions.count() == 0:
        # Create subscription for tech mahindra
        start_date = date.today()
        end_date = start_date + timedelta(days=365)
        
        subscription = Subscription.objects.create(
            company=tech_mahindra,
            plan=tech_mahindra.plan,
            status='active',
            billing_cycle='monthly',
            start_date=start_date,
            end_date=end_date,
            next_billing_date=start_date + timedelta(days=30),
            base_price=tech_mahindra.plan.price,
            discount_amount=0.00,
            tax_amount=0.00,
            total_amount=tech_mahindra.plan.price
        )
        
        print(f'Created subscription: {subscription}')
        print(f'Subscription ID: {subscription.id}')
        print(f'Status: {subscription.status}')
        print(f'Plan: {subscription.plan.name}')
        print(f'Start: {subscription.start_date}')
        print(f'End: {subscription.end_date}')
    else:
        print('Company already has subscriptions or no plan assigned')
else:
    print('Tech Mahindra company not found')

print('\n=== Final Status ===')
companies = Company.objects.all()
for company in companies:
    active_subs = company.subscriptions.filter(status='active')
    print(f'{company.name}: {active_subs.count()} active subscription(s)')
