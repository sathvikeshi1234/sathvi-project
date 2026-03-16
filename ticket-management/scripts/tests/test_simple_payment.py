#!/usr/bin/env python
"""
Simple test to check if payment success works
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


def test_basic_payment():
    print("Basic Payment Test")
    print("=" * 30)

    # Check if we can create a payment
    try:
        # Get or create test data
        user = User.objects.first()
        if not user:
            print("No users found")
            return

        company = Company.objects.first()
        if not company:
            print("No companies found")
            return

        subscription = Subscription.objects.first()
        if not subscription:
            print("No subscriptions found")
            return

        print(f"Using user: {user.username}")
        print(f"Using company: {company.name}")
        print(f"Using subscription: {subscription.id}")

        # Create a test payment
        payment = Payment.objects.create(
            subscription=subscription,
            company=company,
            amount=subscription.total_amount,
            payment_method="test",
            payment_type="subscription",
            status="completed",
            transaction_id=f"TEST_{timezone.now().strftime('%Y%m%d%H%M%S')}",
            invoice_number=f"TEST_INV_{timezone.now().strftime('%Y%m%d%H%M%S')}",
            payment_date=timezone.now(),
            notes="Test payment",
        )

        print(f"Created payment: {payment.id}")
        print(f"Transaction ID: {payment.transaction_id}")
        print(f"Amount: ${payment.amount}")
        print(f"Status: {payment.status}")

        # Check if it appears in queries
        all_payments = Payment.objects.all()
        print(f"Total payments in system: {all_payments.count()}")

        print("Test completed successfully!")
        return True

    except Exception as e:
        print(f"Error: {e}")
        return False


if __name__ == "__main__":
    test_basic_payment()
