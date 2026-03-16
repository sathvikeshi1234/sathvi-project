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

from superadmin.models import Company, Subscription, Plan
from django.utils import timezone

print("=== DEBUGGING PREE AND PRASSU ===")
print()

today = timezone.now().date()

# Check pree Company (ID: 16)
pree = Company.objects.get(id=16)
print(f"PREE Company:")
print(f"  Name: {pree.name}")
print(f"  Plan: {pree.plan.name if pree.plan else 'None'}")
print(f"  Plan ID: {pree.plan.id if pree.plan else 'None'}")

pree_subs = pree.subscriptions.all()
print(f"  Subscriptions: {pree_subs.count()}")
for sub in pree_subs:
    print(
        f"    - ID: {sub.id}, Status: {sub.status}, Plan: {sub.plan.name if sub.plan else 'None'}, End: {sub.end_date}"
    )

print()

# Check prassu Company (ID: 17)
prassu = Company.objects.get(id=17)
print(f"PRASSU Company:")
print(f"  Name: {prassu.name}")
print(f"  Plan: {prassu.plan.name if prassu.plan else 'None'}")
print(f"  Plan ID: {prassu.plan.id if prassu.plan else 'None'}")

prassu_subs = prassu.subscriptions.all()
print(f"  Subscriptions: {prassu_subs.count()}")
for sub in prassu_subs:
    print(
        f"    - ID: {sub.id}, Status: {sub.status}, Plan: {sub.plan.name if sub.plan else 'None'}, End: {sub.end_date}"
    )

print()
print("=== CHECKING SUBSCRIPTION PLAN RELATIONSHIPS ===")
print()

# Check if subscription plans are different from company plans
for company_name in ["pree Company", "prassu Company"]:
    company = Company.objects.get(name=company_name)
    print(f"{company.name}:")
    print(f"  Company plan: {company.plan.name if company.plan else 'None'}")

    for sub in company.subscriptions.all():
        print(f"  Subscription plan: {sub.plan.name if sub.plan else 'None'}")
        print(
            f"  Plans match: {company.plan == sub.plan if company.plan and sub.plan else 'N/A'}"
        )
    print()
