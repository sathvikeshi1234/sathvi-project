#!/usr/bin/env python
"""
Debug script to check payment modal logic
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


def debug_modal_logic():
    print("DEBUG: Payment Modal Logic Check")
    print("=" * 40)

    # Get all users
    users = User.objects.all()
    print(f"Total users: {users.count()}")

    for user in users[:3]:  # Check first 3 users
        print(f"\n--- User: {user.username} ---")
        print(f"Email: {user.email}")
        print(f"Is Staff: {user.is_staff}")
        print(f"Is Superuser: {user.is_superuser}")

        # Check user profile
        try:
            profile = user.userprofile
            print(f"Profile Role: {profile.role.name if profile.role else 'None'}")
        except:
            print("Profile: None")

        # Check company
        expected_company = f"{user.username} Company"
        company = Company.objects.filter(name=expected_company).first()

        if company:
            print(f"Company: {company.name}")
            subscriptions = company.subscriptions.all()
            print(f"Subscriptions: {subscriptions.count()}")
            for sub in subscriptions:
                print(f"  - {sub.id}: {sub.status}")
        else:
            print(f"Company: None (expected: {expected_company})")

        # Test subscription expiry check
        try:
            result = check_subscription_expiry(user)
            print(f"check_subscription_expiry result: {result}")
            print(f"Should show modal: {result}")
        except Exception as e:
            print(f"Error in check_subscription_expiry: {e}")

    print(f"\n--- Test Force Modal URL ---")
    print("Add this to your admin dashboard URL to force modal:")
    print("?show_payment_modal=true")


if __name__ == "__main__":
    debug_modal_logic()
