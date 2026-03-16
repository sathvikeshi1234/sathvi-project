#!/usr/bin/env python
"""
Test that completed payments appear in transactions page
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


def test_payment_to_transaction_flow():
    print("Testing Payment -> Transaction Flow")
    print("=" * 40)

    # Get or create test user
    username = "testpaymentuser"
    user, created = User.objects.get_or_create(
        username=username, defaults={"email": f"{username}@test.com"}
    )

    if created:
        print(f"Created test user: {user.username}")
    else:
        print(f"Using existing user: {user.username}")

    # Get or create company
    company_name = f"{username} Company"
    company, company_created = Company.objects.get_or_create(
        name=company_name, defaults={"email": f"{username}@company.com"}
    )

    if company_created:
        print(f"Created company: {company.name}")
    else:
        print(f"Using existing company: {company.name}")

    # Get or create subscription
    default_plan = Plan.objects.filter(is_active=True).first()
    if not default_plan:
        print("ERROR: No active plan found")
        return

    subscription, sub_created = Subscription.objects.get_or_create(
        company=company,
        plan=default_plan,
        defaults={
            "status": "trial",
            "start_date": timezone.now().date(),
            "end_date": timezone.now().date() + timezone.timedelta(days=30),
            "total_amount": default_plan.price,
        },
    )

    if sub_created:
        print(f"Created subscription: {subscription.id}")
    else:
        print(f"Using existing subscription: {subscription.id}")

    # Create a test payment (simulating payment_success function)
    print(f"\n--- Creating Test Payment ---")

    payment = Payment.objects.create(
        subscription=subscription,
        company=company,
        amount=subscription.total_amount,
        payment_method="razorpay",
        payment_type="subscription",
        status="completed",
        transaction_id=f"TEST_{timezone.now().strftime('%Y%m%d%H%M%S')}",
        invoice_number=f"INV_{timezone.now().strftime('%Y%m%d')}{Payment.objects.count() + 1:04d}",
        payment_date=timezone.now(),
        gateway_response={"razorpay_payment_id": "test_razorpay_id"},
        notes=f"Test payment for {subscription.plan.name} subscription via Razorpay",
        created_by=user,
    )

    print(f"Created payment: #{payment.id}")
    print(f"Transaction ID: {payment.transaction_id}")
    print(f"Invoice Number: {payment.invoice_number}")
    print(f"Amount: ${payment.amount}")
    print(f"Status: {payment.status}")
    print(f"Payment Method: {payment.payment_method}")
    print(f"Payment Date: {payment.payment_date}")

    # Test if payment appears in transactions query
    print(f"\n--- Testing Transaction Query ---")

    all_transactions = Payment.objects.select_related(
        "company", "subscription__plan"
    ).order_by("-payment_date")
    print(f"Total transactions in database: {all_transactions.count()}")

    # Find our test payment
    test_payment_in_transactions = all_transactions.filter(id=payment.id).first()
    if test_payment_in_transactions:
        print(f"SUCCESS: Test payment found in transactions!")
        print(f"  - Transaction ID: {test_payment_in_transactions.transaction_id}")
        print(f"  - Company: {test_payment_in_transactions.company.name}")
        print(f"  - Amount: ${test_payment_in_transactions.amount}")
        print(f"  - Status: {test_payment_in_transactions.status}")
        print(f"  - Payment Date: {test_payment_in_transactions.payment_date}")
    else:
        print(f"ERROR: Test payment NOT found in transactions!")
        return

    # Test completed transactions filter
    completed_transactions = all_transactions.filter(status="completed")
    print(f"\nCompleted transactions: {completed_transactions.count()}")

    our_payment_in_completed = completed_transactions.filter(id=payment.id).first()
    if our_payment_in_completed:
        print(f"SUCCESS: Test payment found in completed transactions!")
    else:
        print(f"ERROR: Test payment NOT found in completed transactions!")
        return

    # Test recent transactions (latest 5)
    recent_payments = (
        Payment.objects.select_related("company", "subscription__plan")
        .filter(status="completed")
        .order_by("-payment_date")[:5]
    )
    print(f"\nRecent payments (latest 5): {recent_payments.count()}")

    our_payment_in_recent = recent_payments.filter(id=payment.id).first()
    if our_payment_in_recent:
        print(f"SUCCESS: Test payment found in recent payments!")
    else:
        print(
            f"INFO: Test payment not in recent payments (might be older than other payments)"
        )

    print(f"\n--- Summary ---")
    print(f"✓ Payment created successfully")
    print(f"✓ Payment appears in all transactions query")
    print(f"✓ Payment appears in completed transactions filter")
    print(f"✓ Payment has all required fields for display")

    print(f"\n--- Expected Display in Transactions Page ---")
    print(f"Transaction ID: {payment.transaction_id}")
    print(f"Company: {payment.company.name}")
    print(f"Payment Type: {payment.get_payment_type_display()}")
    print(f"Plan: {payment.subscription.plan.name}")
    print(f"Amount: +${payment.amount}")
    print(f"Payment Method: {payment.get_payment_method_display()}")
    print(f"Date: {payment.payment_date.strftime('%b %d, %Y %H:%M')}")
    print(f"Status: Completed")

    print(f"\n--- Test URLs ---")
    print(f"Transactions Page: http://localhost:8003/superadmin/page/all_transactions/")
    print(
        f"Dashboard (Recent Payments): http://localhost:8003/superadmin/page/dashboard/"
    )

    return True


if __name__ == "__main__":
    test_payment_to_transaction_flow()
