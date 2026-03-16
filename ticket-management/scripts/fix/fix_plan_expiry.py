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

from superadmin.models import Company

print("=== FIXING PLAN EXPIRY INCONSISTENCY ===")
print()

# Find companies that have plan_expiry_date but no plan
companies_with_expiry_no_plan = Company.objects.filter(plan__isnull=True).exclude(
    plan_expiry_date__isnull=True
)

print(
    f"Found {companies_with_expiry_no_plan.count()} companies with expiry date but no plan"
)
print()

for company in companies_with_expiry_no_plan:
    print(f"Fixing {company.name}:")
    print(
        f'  Before: Plan="{company.plan.name if company.plan else "None"}", Expiry="{company.plan_expiry_date}"'
    )

    # Clear the expiry date since there's no plan
    company.plan_expiry_date = None
    company.save()

    print(
        f'  After:  Plan="{company.plan.name if company.plan else "None"}", Expiry="{company.plan_expiry_date}"'
    )
    print(f"  + Fixed")
    print()

print("=== VERIFICATION ===")
print()

# Verify the fix
remaining_issues = Company.objects.filter(plan__isnull=True).exclude(
    plan_expiry_date__isnull=True
)

print(f"Remaining companies with expiry date but no plan: {remaining_issues.count()}")

if remaining_issues.count() == 0:
    print("✓ All issues fixed!")
else:
    print("⚠ Some issues remain")
    for company in remaining_issues:
        print(f"  - {company.name}")
