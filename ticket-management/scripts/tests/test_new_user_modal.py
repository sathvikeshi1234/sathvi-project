#!/usr/bin/env python
"""
Test script to check why payment modal is not showing for new users
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


def test_new_user_scenario():
    print("Testing New User Payment Modal Scenario")
    print("=" * 50)

    # Get a test user (or create one)
    username = "testnewuser123"
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            "email": f"{username}@test.com",
            "first_name": "Test",
            "last_name": "User",
        },
    )

    if created:
        print(f"✓ Created new test user: {user.username}")
    else:
        print(f"✓ Using existing test user: {user.username}")

    # Check if user has the required role
    print(f"\n📋 User Details:")
    print(f"  Username: {user.username}")
    print(f"  Email: {user.email}")
    print(f"  Is Staff: {user.is_staff}")
    print(f"  Is Superuser: {user.is_superuser}")

    # Check if user has profile
    try:
        profile = user.userprofile
        print(f"  Profile Role: {profile.role.name if profile.role else 'None'}")
    except:
        print("  Profile: None")

    # Check companies
    companies = Company.objects.all()
    print(f"\n🏢 Companies in database: {companies.count()}")
    for company in companies:
        print(f"  - {company.name}")

    # Check if user's company exists
    expected_company_name = f"{user.username} Company"
    user_company = Company.objects.filter(name=expected_company_name).first()

    if user_company:
        print(f"\n✓ Found user's company: {user_company.name}")
        subscriptions = user_company.subscriptions.all()
        print(f"  Subscriptions: {subscriptions.count()}")
        for sub in subscriptions:
            print(
                f"    - ID: {sub.id}, Status: {sub.status}, Plan: {sub.plan.name if sub.plan else 'None'}"
            )
    else:
        print(f"\n❌ No company found named: {expected_company_name}")

    # Test the subscription expiry check function
    print(f"\n🔍 Testing check_subscription_expiry function:")
    try:
        result = check_subscription_expiry(user)
        print(f"  Result: {result}")
        print(f"  Should show modal: {result}")
    except Exception as e:
        print(f"  Error: {e}")
        import traceback

        traceback.print_exc()

    print(f"\n📊 Summary:")
    print(f"  User exists: ✓")
    print(f"  Company exists: {'✓' if user_company else '❌'}")
    print(
        f"  check_subscription_expiry returns: {result if 'result' in locals() else 'Unknown'}"
    )

    print(f"\n🧪 Test URL:")
    print(f"  http://localhost:8000/dashboard/admin-dashboard/?show_payment_modal=true")
    print(f"  (Add this parameter to force the modal to show)")

    return result if "result" in locals() else False


if __name__ == "__main__":
    test_new_user_scenario()
