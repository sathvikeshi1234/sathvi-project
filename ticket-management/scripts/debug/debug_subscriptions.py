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

print("=== DEBUG SUBSCRIPTIONS ===")
print()

today = timezone.now().date()
print(f"Today: {today}")
print()

companies = Company.objects.all()
print(f"Total companies: {companies.count()}")
print()

for company in companies:
    print(f"Company: {company.name} (ID: {company.id})")
    print(f"  Plan: {company.plan.name if company.plan else 'None'}")

    subscriptions = company.subscriptions.all()
    print(f"  Total subscriptions: {subscriptions.count()}")

    for sub in subscriptions:
        print(f"    - ID: {sub.id}")
        print(f"      Status: {sub.status}")
        print(f"      Start: {sub.start_date}")
        print(f"      End: {sub.end_date}")
        print(f"      Plan: {sub.plan.name if sub.plan else 'None'}")
        print(
            f"      End >= Today: {sub.end_date >= today if sub.end_date else 'No end date'}"
        )
        print(f"      Status != cancelled: {sub.status != 'cancelled'}")

    # Test the exact query from the view
    active_sub = (
        company.subscriptions.filter(end_date__gte=today)
        .exclude(status="cancelled")
        .order_by("-end_date")
        .first()
    )
    print(f"  Active sub query result: {active_sub}")
    print()
