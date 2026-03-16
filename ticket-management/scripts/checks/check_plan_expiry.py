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

from superadmin.models import Company, Plan
from django.utils import timezone

print("=== CHECKING PLAN EXPIRY INCONSISTENCY ===")
print()

# Find companies that have plan_expiry_date but no plan
companies_with_expiry_no_plan = Company.objects.filter(plan__isnull=True).exclude(
    plan_expiry_date__isnull=True
)

print(
    f"Companies with expiry date but no plan: {companies_with_expiry_no_plan.count()}"
)
print()

for company in companies_with_expiry_no_plan:
    print(f"Company: {company.name}")
    print(f"  Plan: {company.plan.name if company.plan else 'None'}")
    print(f"  Plan Expiry Date: {company.plan_expiry_date}")
    print()

print("=== ALL COMPANIES WITH PLAN EXPIRY DATES ===")
print()

all_with_expiry = Company.objects.exclude(plan_expiry_date__isnull=True)
print(f"Total companies with expiry dates: {all_with_expiry.count()}")
print()

for company in all_with_expiry:
    print(f"{company.name}:")
    print(f"  Plan: {company.plan.name if company.plan else 'None'}")
    print(f"  Expiry: {company.plan_expiry_date}")
    print(
        f"  Status: {'Expired' if company.plan_expiry_date and company.plan_expiry_date < timezone.now().date() else 'Valid'}"
    )
    print()
