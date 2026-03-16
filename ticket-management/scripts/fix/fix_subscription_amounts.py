#!/usr/bin/env python
"""
Fix all subscriptions with $0.00 amounts
"""

import os
import sys
from pathlib import Path
import django

# Setup Django
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from superadmin.models import Subscription, Plan


def fix_subscription_amounts():
    print("Fixing Subscription Amounts")
    print("=" * 40)

    # Find all subscriptions with $0.00 total_amount
    zero_subscriptions = Subscription.objects.filter(total_amount=0.00)
    print(f"Found {zero_subscriptions.count()} subscriptions with $0.00 amount")

    fixed_count = 0
    for subscription in zero_subscriptions:
        print(f"\nFixing Subscription #{subscription.id}:")
        print(f"  Company: {subscription.company.name}")
        print(f"  Plan: {subscription.plan.name}")
        print(f"  Plan Price: ${subscription.plan.price}")
        print(f"  Current Total Amount: ${subscription.total_amount}")

        # Fix the subscription amounts
        subscription.base_price = subscription.plan.price
        subscription.discount_amount = 0.00
        subscription.tax_amount = 0.00
        subscription.total_amount = subscription.plan.price
        subscription.save()

        print(f"  Fixed Total Amount: ${subscription.total_amount}")
        fixed_count += 1

    print(f"\nFixed {fixed_count} subscriptions")

    # Verify the fix
    remaining_zero = Subscription.objects.filter(total_amount=0.00).count()
    print(f"Remaining subscriptions with $0.00: {remaining_zero}")

    if remaining_zero == 0:
        print("SUCCESS: All subscription amounts have been fixed!")
    else:
        print(f"WARNING: {remaining_zero} subscriptions still have $0.00 amount")

    return fixed_count


if __name__ == "__main__":
    fix_subscription_amounts()
