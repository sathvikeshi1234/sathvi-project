#!/usr/bin/env python
import os
import sys
from pathlib import Path
import django

# Add the project root to the Python path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Setup Django
django.setup()

from superadmin.models import Plan

print("=== CLEANING UP UNAUTHORIZED PLANS ===")
print()

# Define the three allowed plan names
ALLOWED_PLANS = ["Basic", "Standard", "Premium"]

# Get all plans
all_plans = Plan.objects.all()
print(f"Total plans in database: {all_plans.count()}")
print()

# Find unauthorized plans
unauthorized_plans = all_plans.exclude(name__in=ALLOWED_PLANS)
print(f"Unauthorized plans to remove: {unauthorized_plans.count()}")
print()

for plan in unauthorized_plans:
    print(f"Removing: {plan.name} (ID: {plan.id})")
    plan.delete()

print()

# Ensure the three allowed plans exist
for plan_name in ALLOWED_PLANS:
    plan = Plan.objects.filter(name__iexact=plan_name).first()
    if plan:
        print(f"✓ {plan_name} exists (ID: {plan.id})")
    else:
        print(f"⚠ {plan_name} does not exist - you may need to create it")

print()
print("=== FINAL PLAN LIST ===")
print()

final_plans = Plan.objects.filter(name__in=ALLOWED_PLANS).order_by("name")
for plan in final_plans:
    print(
        f"{plan.name}: ${plan.price} ({plan.billing_cycle}) - {plan.users} users, {plan.storage} storage"
    )
