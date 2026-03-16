#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from superadmin.models import Company, Plan

print("=== PLANS ===")
plans = Plan.objects.all()
for plan in plans:
    print(f"ID: {plan.id}, Name: {plan.name}, Status: {plan.status}")

print("\n=== COMPANIES ===")
companies = Company.objects.select_related('plan').all()
for company in companies:
    plan_name = company.plan.name if company.plan else "None"
    print(f"Company: {company.name}, Plan: {plan_name}, Status: {company.subscription_status}")

print(f"\nTotal companies: {len(companies)}")
print(f"Total plans: {len(plans)}")
