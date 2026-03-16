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

print("=== FIXING COMPANY PLAN INCONSISTENCY ===")
print()

today = timezone.now().date()

# Find companies that have subscriptions but no plan set
companies_with_sub_no_plan = (
    Company.objects.filter(plan__isnull=True)
    .filter(subscriptions__isnull=False)
    .distinct()
)

print(f"Companies with subscriptions but no plan: {companies_with_sub_no_plan.count()}")
print()

for company in companies_with_sub_no_plan:
    # Get the most recent active subscription
    active_sub = (
        company.subscriptions.filter(end_date__gte=today)
        .exclude(status="cancelled")
        .order_by("-end_date")
        .first()
    )

    if active_sub and active_sub.plan:
        print(f"Updating {company.name}:")
        print(f"  From plan: {company.plan.name if company.plan else 'None'}")
        print(f"  To plan: {active_sub.plan.name}")

        company.plan = active_sub.plan
        company.save()

        print(f"  + Updated")
    else:
        print(f"{company.name}: No active subscription found to sync plan")
    print()

print("=== VERIFICATION ===")
print()

for company in companies_with_sub_no_plan:
    company.refresh_from_db()
    print(f"{company.name}: Plan = {company.plan.name if company.plan else 'None'}")
