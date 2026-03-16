#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from superadmin.models import Plan

demo_plans = [
    {
        'name': 'Basic',
        'price': 29.00,
        'billing_cycle': 'monthly',
        'users': 5,
        'storage': '10GB',
        'status': 'active',
    },
    {
        'name': 'Standard',
        'price': 99.00,
        'billing_cycle': 'monthly',
        'users': 15,
        'storage': '50GB',
        'status': 'active',
    },
    {
        'name': 'Premium',
        'price': 199.00,
        'billing_cycle': 'monthly',
        'users': 999,  # Unlimited (using a high number)
        'storage': '200GB',
        'status': 'active',
    },
]

print("Creating demo plans...")
for plan_data in demo_plans:
    plan, created = Plan.objects.get_or_create(
        name=plan_data['name'],
        defaults=plan_data
    )
    if created:
        print(f"Created plan: {plan.name}")
    else:
        print(f"Plan already exists: {plan.name}")

print("Demo plans created successfully!")
