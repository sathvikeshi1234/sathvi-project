#!/usr/bin/env python
"""
Test why payment modal is not showing for admin users
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
from superadmin.models import Company, Subscription
from superadmin.views import check_subscription_expiry


def test_admin_user(username):
    print(f"Testing admin user: {username}")
    print("=" * 40)

    # Get user
    try:
        user = User.objects.get(username=username)
        print(f"User found: {user.username}")
        print(f"Email: {user.email}")
        print(f"Is Staff: {user.is_staff}")
        print(f"Is Superuser: {user.is_superuser}")
    except User.DoesNotExist:
        print(f"User {username} not found")
        return

    # Check user profile
    try:
        profile = user.userprofile
        print(f"Profile Role: {profile.role.name if profile.role else 'None'}")
    except:
        print("Profile: None")

    # Check company
    expected_company = f"{username} Company"
    company = Company.objects.filter(name=expected_company).first()

    if company:
        print(f"\nCompany: {company.name}")
        print(f"Subscription Status: {company.subscription_status}")
        print(f"Plan Expiry: {company.plan_expiry_date}")

        subscriptions = company.subscriptions.all()
        print(f"Subscriptions: {subscriptions.count()}")
        for sub in subscriptions:
            print(f"  - ID: {sub.id}")
            print(f"    Status: {sub.status}")
            print(f"    Plan: {sub.plan.name if sub.plan else 'None'}")
            print(f"    Start: {sub.start_date}")
            print(f"    End: {sub.end_date}")
            print(f"    Amount: {sub.total_amount}")
    else:
        print(f"\nCompany: None (expected: {expected_company})")

    # Test subscription expiry check
    print(f"\n--- Subscription Expiry Check ---")
    try:
        result = check_subscription_expiry(user)
        print(f"check_subscription_expiry result: {result}")
        print(f"Should show modal: {result}")

        if result:
            print(f"\n✅ Modal SHOULD show for user {username}")
        else:
            print(f"\n❌ Modal will NOT show for user {username}")
            print(f"Reason: User has active subscription")

    except Exception as e:
        print(f"Error in check_subscription_expiry: {e}")
        import traceback

        traceback.print_exc()

    print(f"\n--- Test URLs ---")
    print(f"Admin Dashboard: http://localhost:8003/dashboard/admin-dashboard/")
    print(
        f"Force Modal: http://localhost:8003/dashboard/admin-dashboard/?show_payment_modal=true"
    )
    print(
        f"Clear Modal: http://localhost:8003/dashboard/admin-dashboard/?clear_modal=true"
    )


if __name__ == "__main__":
    # Test with your admin username - change this to your actual admin username
    test_admin_user("sathvika.arikatla")  # Change this to your admin username
