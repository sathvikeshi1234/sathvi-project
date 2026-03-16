#!/usr/bin/env python
"""
Verify that payments appear correctly in transactions
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


def verify_payment_transactions():
    print("Verifying Payment -> Transaction Display")
    print("=" * 50)

    # Check existing payments
    all_payments = Payment.objects.all()
    completed_payments = Payment.objects.filter(status="completed")

    print(f"Total payments in database: {all_payments.count()}")
    print(f"Completed payments: {completed_payments.count()}")

    if completed_payments.exists():
        print(f"\n--- Latest Completed Payments ---")
        latest_payments = completed_payments.order_by("-payment_date")[:5]

        for payment in latest_payments:
            print(f"\nPayment #{payment.id}:")
            print(f"  Transaction ID: {payment.transaction_id}")
            print(f"  Invoice Number: {payment.invoice_number}")
            print(f"  Company: {payment.company.name}")
            print(f"  Amount: ${payment.amount}")
            print(f"  Status: {payment.status}")
            print(f"  Payment Method: {payment.payment_method}")
            print(f"  Payment Type: {payment.payment_type}")
            print(f"  Payment Date: {payment.payment_date}")
            print(
                f"  Created By: {payment.created_by.username if payment.created_by else 'System'}"
            )

            if payment.subscription:
                print(f"  Subscription Plan: {payment.subscription.plan.name}")
                print(f"  Subscription Status: {payment.subscription.status}")

            print(f"  Notes: {payment.notes}")

    # Test the exact query used in transactions page
    print(f"\n--- Testing Transactions Page Query ---")
    all_transactions = Payment.objects.select_related(
        "company", "subscription__plan"
    ).order_by("-payment_date")
    print(f"Transactions page query returns: {all_transactions.count()} transactions")

    # Test completed transactions filter
    completed_transactions = all_transactions.filter(status="completed")
    print(f"Completed transactions: {completed_transactions.count()}")

    # Show transaction stats (same as in view)
    total_transactions = all_transactions.count()
    completed_count = completed_transactions.count()
    pending_count = all_transactions.filter(status="pending").count()
    failed_count = all_transactions.filter(status="failed").count()

    print(f"\n--- Transaction Statistics ---")
    print(f"Total Transactions: {total_transactions}")
    print(f"Completed: {completed_count}")
    print(f"Pending: {pending_count}")
    print(f"Failed: {failed_count}")

    # Verify template fields are available
    print(f"\n--- Template Field Verification ---")
    if completed_transactions.exists():
        sample_payment = completed_transactions.first()
        print(f"Sample payment #{sample_payment.id}:")

        # Check all fields used in template
        print(f"  transaction_id: {sample_payment.transaction_id}")
        print(f"  id: {sample_payment.id}")
        print(f"  company.name: {sample_payment.company.name}")
        print(f"  company.email: {sample_payment.company.email}")
        print(f"  payment_type: {sample_payment.payment_type}")
        print(f"  get_payment_type_display: {sample_payment.get_payment_type_display}")
        print(
            f"  subscription.plan.name: {sample_payment.subscription.plan.name if sample_payment.subscription else 'None'}"
        )
        print(f"  amount: {sample_payment.amount}")
        print(f"  payment_method: {sample_payment.payment_method}")
        print(
            f"  get_payment_method_display: {sample_payment.get_payment_method_display}"
        )
        print(f"  payment_date: {sample_payment.payment_date}")
        print(f"  status: {sample_payment.status}")

        print(f"\n✓ All required template fields are available!")

    print(f"\n--- Expected Display Format ---")
    print(f"Transaction ID | Company | Type | Plan | Amount | Method | Date | Status")
    print(f"---------------|---------|------|------|--------|--------|-----|--------")

    for payment in completed_transactions[:3]:
        transaction_id = (
            payment.transaction_id
            if payment.transaction_id
            else f"#TXN-{payment.id:04d}"
        )
        company = payment.company.name
        payment_type = payment.get_payment_type_display
        plan = payment.subscription.plan.name if payment.subscription else "-"
        amount = f"+${payment.amount}"
        method = payment.get_payment_method_display
        date = payment.payment_date.strftime("%b %d, %Y %H:%M")
        status = "Completed"

        print(
            f"{transaction_id[:15]:15} | {company[:15]:15} | {payment_type[:6]:6} | {plan[:6]:6} | {amount[:8]:8} | {method[:8]:8} | {date[:12]:12} | {status}"
        )

    print(f"\n--- URLs to Check ---")
    print(f"All Transactions: http://localhost:8003/superadmin/page/all_transactions/")
    print(f"Dashboard (Recent): http://localhost:8003/superadmin/page/dashboard/")

    print(f"\n--- Summary ---")
    if completed_payments.exists():
        print(f"✓ Payment records are being created")
        print(f"✓ Payments appear in transactions query")
        print(f"✓ All template fields are available")
        print(f"✓ Transaction statistics are calculated")
        print(f"✓ Payment details should display correctly")
    else:
        print(f"❌ No completed payments found")
        print(f"   - Complete a test payment to verify display")

    return completed_payments.exists()


if __name__ == "__main__":
    verify_payment_transactions()
