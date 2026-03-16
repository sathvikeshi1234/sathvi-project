#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from superadmin.models import Plan

print('=== Current Plans Analysis ===')

all_plans = Plan.objects.all()
print(f'Total plans: {all_plans.count()}')
print()

print('All Current Plans:')
for plan in all_plans:
    print(f'ID: {plan.id} | Name: {plan.name} | Price: ${plan.price} | Status: {plan.status} | Active: {plan.is_active}')

print('\n=== Cleaning Up Plans ===')

# Keep only Basic, Standard, Premium plans
allowed_plans = ['Basic', 'Standard', 'Premium']
plans_to_keep = []
plans_to_deactivate = []

for plan in all_plans:
    if plan.name in allowed_plans:
        plans_to_keep.append(plan)
        print(f'KEEP: {plan.name} (ID: {plan.id})')
    else:
        plans_to_deactivate.append(plan)
        print(f'DEACTIVATE: {plan.name} (ID: {plan.id})')

# Deactivate unwanted plans
for plan in plans_to_deactivate:
    plan.is_active = False
    plan.status = 'inactive'
    plan.save()
    print(f'Deactivated: {plan.name}')

# Ensure the three main plans exist and are active
main_plans_data = [
    {'name': 'Basic', 'price': 29.00, 'users': 5, 'storage': '10GB', 'billing_cycle': 'monthly'},
    {'name': 'Standard', 'price': 99.00, 'users': 20, 'storage': '100GB', 'billing_cycle': 'monthly'},
    {'name': 'Premium', 'price': 199.00, 'users': 50, 'storage': '500GB', 'billing_cycle': 'monthly'}
]

for plan_data in main_plans_data:
    # Find existing plans with this name (case-insensitive)
    existing_plans = Plan.objects.filter(name__iexact=plan_data['name'])
    
    if existing_plans.exists():
        # Keep the first one, deactivate others
        main_plan = existing_plans.first()
        other_plans = existing_plans.exclude(id=main_plan.id)
        
        # Deactivate duplicates
        for other_plan in other_plans:
            other_plan.is_active = False
            other_plan.status = 'inactive'
            other_plan.save()
            print(f'Deactivated duplicate: {other_plan.name} (ID: {other_plan.id})')
        
        # Activate the main plan
        main_plan.status = 'active'
        main_plan.is_active = True
        main_plan.price = plan_data['price']
        main_plan.users = plan_data['users']
        main_plan.storage = plan_data['storage']
        main_plan.billing_cycle = plan_data['billing_cycle']
        main_plan.save()
        print(f'Activated/Updated: {main_plan.name} (ID: {main_plan.id})')
    else:
        # Create new plan
        plan = Plan.objects.create(
            name=plan_data['name'],
            price=plan_data['price'],
            users=plan_data['users'],
            storage=plan_data['storage'],
            billing_cycle=plan_data['billing_cycle'],
            status='active',
            is_active=True
        )
        print(f'Created new plan: {plan.name} (ID: {plan.id})')

print('\n=== Final Plan Status ===')
active_plans = Plan.objects.filter(is_active=True, status='active')
print(f'Active plans: {active_plans.count()}')

for plan in active_plans.order_by('name'):
    print(f'{plan.name}: ${plan.price} - {plan.users} users - {plan.storage}')
