#!/usr/bin/env python
"""
Simple debug script to check payment flow
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

from django.contrib.auth.models import User
from superadmin.models import Company, Subscription, Payment, Plan
from django.utils import timezone


def debug_payment_system():
    print("DEBUG: Payment System Check")
    print("=" * 40)

    # Check models exist
    try:
        print(f"Users: {User.objects.count()}")
        print(f"Companies: {Company.objects.count()}")
        print(f"Subscriptions: {Subscription.objects.count()}")
        print(f"Payments: {Payment.objects.count()}")
        print(f"Plans: {Plan.objects.count()}")
    except Exception as e:
        print(f"Error checking models: {e}")
        return

    # Check payment_success function exists
    try:
        from superadmin.views import payment_success

        print("✓ payment_success function exists")
    except ImportError as e:
        print(f"✗ payment_success function not found: {e}")
        return

    # Check if there are any recent payments
    recent_payments = Payment.objects.order_by("-created_at")[:5]
    print(f"\nRecent payments: {len(recent_payments)}")
    for payment in recent_payments:
        print(f"  - {payment.transaction_id} - ${payment.amount} - {payment.status}")

    print("\nDEBUG: Payment system check complete")


if __name__ == "__main__":
    debug_payment_system()
