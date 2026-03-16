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

print("=== CLEANING DUPLICATE PLANS ===")
print()

# Find duplicate Basic plans
basic_plans = Plan.objects.filter(name__iexact="Basic").order_by("id")
print(f"Found {basic_plans.count()} Basic plans")

if basic_plans.count() > 1:
    # Keep the first one, delete the rest
    keep_plan = basic_plans.first()
    delete_plans = basic_plans.exclude(id=keep_plan.id)

    print(f"Keeping: Basic (ID: {keep_plan.id})")
    print("Deleting duplicates:")

    for plan in delete_plans:
        print(f"  - Basic (ID: {plan.id})")
        plan.delete()

    print("Duplicates cleaned up!")
else:
    print("No duplicate Basic plans found")

print()
print("=== FINAL PLANS ===")
print()

all_plans = Plan.objects.all().order_by("name")
for plan in all_plans:
    print(
        f"{plan.name} (ID: {plan.id}): ${plan.price or '0.00'} - {plan.billing_cycle}"
    )
