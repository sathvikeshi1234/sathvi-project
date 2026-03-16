#!/usr/bin/env python
import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from superadmin.models import Company, Plan

print("Assigning plans to companies...")

companies = Company.objects.filter(plan__isnull=True)
plans = Plan.objects.filter(status='active')

if not plans.exists():
    print("No active plans found!")
else:
    plan_list = list(plans)
    
    for i, company in enumerate(companies):
        # Assign a plan in round-robin fashion
        plan = plan_list[i % len(plan_list)]
        
        # Set subscription dates
        start_date = date.today()
        expiry_date = start_date + timedelta(days=365)  # 1 year from now
        
        company.plan = plan
        company.subscription_start_date = start_date
        company.plan_expiry_date = expiry_date
        company.subscription_status = 'active'
        company.save()
        
        print(f"Assigned {plan.name} to {company.name}")

print("\nUpdated company list:")
companies = Company.objects.select_related('plan').all()
for company in companies:
    plan_name = company.plan.name if company.plan else "None"
    print(f"Company: {company.name}, Plan: {plan_name}, Status: {company.subscription_status}")
