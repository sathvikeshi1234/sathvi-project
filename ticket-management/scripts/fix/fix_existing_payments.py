#!/usr/bin/env python
"""
Fix existing payments with $0.00 amounts
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

from superadmin.models import Payment


def fix_existing_payments():
    print("Fixing Existing Payments with $0.00 Amounts")
    print("=" * 50)

    # Find payments with $0.00 amounts
    zero_payments = Payment.objects.filter(amount=0.00)
    print(f"Found {zero_payments.count()} payments with $0.00 amount")

    fixed_count = 0
    for payment in zero_payments:
        print(f"\nFixing Payment #{payment.id}:")
        print(f"  Transaction ID: {payment.transaction_id}")
        print(f"  Company: {payment.company.name}")
        print(f"  Current Amount: ${payment.amount}")

        if payment.subscription:
            correct_amount = payment.subscription.plan.price
            print(f"  Plan: {payment.subscription.plan.name}")
            print(f"  Plan Price: ${correct_amount}")

            # Fix the payment amount
            payment.amount = correct_amount
            payment.save()

            print(f"  Fixed Amount: ${payment.amount}")
            fixed_count += 1
        else:
            print(f"  No subscription found - cannot fix amount")

    print(f"\nFixed {fixed_count} payments")

    # Verify the fix
    remaining_zero = Payment.objects.filter(amount=0.00).count()
    print(f"Remaining payments with $0.00: {remaining_zero}")

    if remaining_zero == 0:
        print("SUCCESS: All payment amounts have been fixed!")
    else:
        print(f"WARNING: {remaining_zero} payments still have $0.00 amount")

    return fixed_count


if __name__ == "__main__":
    fix_existing_payments()
