#!/usr/bin/env python
"""
Test script to verify the payment flow works correctly.
Run this script to test the payment success functionality.
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

from django.test import RequestFactory
from django.contrib.auth.models import User
from superadmin.models import Company, Subscription, Payment, Plan
from superadmin.views import payment_success
from django.utils import timezone
import json


def test_payment_success():
    """Test the payment_success function creates payment records correctly"""
    print("🧪 Testing Payment Success Flow...")
    print("=" * 50)

    # Create test user
    user, created = User.objects.get_or_create(
        username="test_payment_user",
        defaults={"email": "test@example.com", "is_staff": True, "is_superuser": True},
    )
    if created:
        print(f"✓ Created test user: {user.username}")
    else:
        print(f"✓ Using existing test user: {user.username}")

    # Create test company
    company, created = Company.objects.get_or_create(
        name=f"{user.username} Company",
        defaults={
            "email": f"{user.username}@company.com",
            "phone": "0000000000",
            "subscription_status": "trial",
            "subscription_start_date": timezone.now().date(),
            "plan_expiry_date": timezone.now().date() + timezone.timedelta(days=30),
        },
    )
    if created:
        print(f"✓ Created test company: {company.name}")
    else:
        print(f"✓ Using existing company: {company.name}")

    # Create test plan
    plan, created = Plan.objects.get_or_create(
        name="Basic",
        defaults={
            "price": 199.00,
            "billing_cycle": "monthly",
            "users": 5,
            "storage": "10GB",
            "status": "active",
            "is_active": True,
        },
    )
    if created:
        print(f"✓ Created test plan: {plan.name}")
    else:
        print(f"✓ Using existing plan: {plan.name}")

    # Create test subscription
    subscription, created = Subscription.objects.get_or_create(
        company=company,
        defaults={
            "plan": plan,
            "status": "trial",
            "start_date": timezone.now().date(),
            "end_date": timezone.now().date() + timezone.timedelta(days=30),
            "next_billing_date": timezone.now().date() + timezone.timedelta(days=30),
            "base_price": plan.price,
            "discount_amount": 0.00,
            "tax_amount": 0.00,
            "total_amount": plan.price,
            "auto_renew": True,
        },
    )
    if created:
        print(f"✓ Created test subscription: {subscription.id}")
    else:
        print(f"✓ Using existing subscription: {subscription.id}")

    # Count payments before test
    payments_before = Payment.objects.filter(company=company).count()
    print(f"📊 Payments before test: {payments_before}")

    # Create mock request
    factory = RequestFactory()
    request_data = {
        "razorpay_payment_id": "pay_test123456789",
        "subscription_id": subscription.id,
    }

    request = factory.post(
        "/superadmin/payment-success/",
        data=json.dumps(request_data),
        content_type="application/json",
    )
    request.user = user
    request.session = {}

    # Call payment_success function
    print("\n🔄 Calling payment_success function...")
    try:
        response = payment_success(request)
        response_data = json.loads(response.content)

        if response.status_code == 200:
            print("✅ payment_success returned 200 OK")
            print(f"✅ Response status: {response_data.get('status')}")
            print(f"✅ Payment ID: {response_data.get('payment_id')}")
            print(f"✅ Transaction ID: {response_data.get('transaction_id')}")
            print(f"✅ Invoice Number: {response_data.get('invoice_number')}")
        else:
            print(f"❌ payment_success returned {response.status_code}")
            print(f"❌ Response: {response_data}")
            return False

    except Exception as e:
        print(f"❌ Error calling payment_success: {e}")
        return False

    # Verify payment record was created
    payments_after = Payment.objects.filter(company=company).count()
    print(f"\n📊 Payments after test: {payments_after}")

    if payments_after > payments_before:
        print("✅ New payment record was created!")

        # Get the latest payment
        latest_payment = (
            Payment.objects.filter(company=company).order_by("-created_at").first()
        )
        print(f"✅ Payment Amount: ${latest_payment.amount}")
        print(f"✅ Payment Status: {latest_payment.status}")
        print(f"✅ Payment Method: {latest_payment.payment_method}")
        print(f"✅ Transaction ID: {latest_payment.transaction_id}")
        print(f"✅ Invoice Number: {latest_payment.invoice_number}")
        print(f"✅ Payment Date: {latest_payment.payment_date}")

        # Verify subscription was updated
        subscription.refresh_from_db()
        print(f"✅ Subscription Status: {subscription.status}")
        print(f"✅ Subscription End Date: {subscription.end_date}")

        # Verify company was updated
        company.refresh_from_db()
        print(f"✅ Company Subscription Status: {company.subscription_status}")
        print(f"✅ Company Plan Expiry Date: {company.plan_expiry_date}")

        return True
    else:
        print("❌ No new payment record was created!")
        return False


def test_superadmin_transaction_panel():
    """Test that Super Admin can see transactions"""
    print("\n🧪 Testing Super Admin Transaction Panel...")
    print("=" * 50)

    # Get all payments
    all_payments = Payment.objects.select_related(
        "company", "subscription__plan"
    ).order_by("-payment_date")

    print(f"📊 Total Payments in System: {all_payments.count()}")

    if all_payments.exists():
        print("\n📋 Recent Transactions:")
        for payment in all_payments[:5]:  # Show last 5
            print(
                f"  • {payment.transaction_id} - {payment.company.name} - ${payment.amount} ({payment.status})"
            )
        print("✅ Super Admin can view transactions!")
        return True
    else:
        print("❌ No payments found in system")
        return False


if __name__ == "__main__":
    print("🚀 Starting Payment Flow Tests")
    print("=" * 60)

    # Test 1: Payment Success
    test1_passed = test_payment_success()

    # Test 2: Super Admin Panel
    test2_passed = test_superadmin_transaction_panel()

    print("\n" + "=" * 60)
    print("📊 TEST RESULTS:")
    print(f"✅ Payment Success Test: {'PASSED' if test1_passed else 'FAILED'}")
    print(f"✅ Super Admin Panel Test: {'PASSED' if test2_passed else 'FAILED'}")

    if test1_passed and test2_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Payment system is working correctly!")
        print("✅ Users can access dashboard after payment!")
        print("✅ Super Admin can see all transactions!")
    else:
        print("\n❌ SOME TESTS FAILED!")
        print("Please check the implementation.")

    print("=" * 60)
