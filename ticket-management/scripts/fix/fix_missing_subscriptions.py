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

print("=== CREATING MISSING SUBSCRIPTIONS ===")
print()

today = timezone.now().date()
companies_with_plan_no_sub = Company.objects.filter(plan__isnull=False).exclude(
    subscriptions__isnull=False
)

print(f"Companies with plan but no subscription: {companies_with_plan_no_sub.count()}")
print()

for company in companies_with_plan_no_sub:
    print(f"Creating subscription for: {company.name} (Plan: {company.plan.name})")

    # Create subscription
    subscription, created = Subscription.objects.get_or_create(
        company=company,
        defaults={
            "plan": company.plan,
            "status": "trial",
            "start_date": today,
            "end_date": today + timezone.timedelta(days=30),
            "next_billing_date": today + timezone.timedelta(days=30),
            "base_price": company.plan.price,
            "discount_amount": 0.00,
            "tax_amount": 0.00,
            "total_amount": company.plan.price,
        },
    )

    if created:
        print(f"  + Subscription created (ID: {subscription.id})")
    else:
        print(f"  - Subscription already exists")

print()
print("=== VERIFICATION ===")
print()

# Verify the results
for company in companies_with_plan_no_sub:
    active_sub = (
        company.subscriptions.filter(end_date__gte=today)
        .exclude(status="cancelled")
        .order_by("-end_date")
        .first()
    )
    print(f"{company.name}: Active subscription = {active_sub is not None}")
