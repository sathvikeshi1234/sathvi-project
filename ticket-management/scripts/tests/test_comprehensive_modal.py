#!/usr/bin/env python
"""
Test comprehensive payment modal logic for all user scenarios
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
from superadmin.views import should_show_payment_modal
from django.utils import timezone


def test_all_scenarios():
    print("Testing Comprehensive Payment Modal Logic")
    print("=" * 50)

    # Test different user scenarios
    test_cases = [
        {
            "name": "New User (No Company)",
            "username": "newuser123",
            "setup": lambda: create_new_user("newuser123"),
        },
        {
            "name": "User with Company but No Subscription",
            "username": "companynosub",
            "setup": lambda: create_company_no_subscription("companynosub"),
        },
        {
            "name": "User with Active Trial",
            "username": "activetrial",
            "setup": lambda: create_active_trial("activetrial"),
        },
        {
            "name": "User with Expired Trial",
            "username": "expiredtrial",
            "setup": lambda: create_expired_trial("expiredtrial"),
        },
        {
            "name": "User with Active Subscription",
            "username": "activeuser",
            "setup": lambda: create_active_subscription("activeuser"),
        },
        {
            "name": "Recent User (Created < 24 hours)",
            "username": "recentuser",
            "setup": lambda: create_recent_user("recentuser"),
        },
        {
            "name": "Trial Expiring Soon (< 7 days)",
            "username": "expiringsoon",
            "setup": lambda: create_trial_expiring_soon("expiringsoon"),
        },
    ]

    results = []

    for test_case in test_cases:
        print(f"\n--- {test_case['name']} ---")

        try:
            # Setup test case
            user = test_case["setup"]()

            # Test the modal logic
            should_show = should_show_payment_modal(user)

            print(f"Username: {user.username}")
            print(f"Should show modal: {should_show}")

            results.append(
                {
                    "test": test_case["name"],
                    "username": user.username,
                    "should_show": should_show,
                }
            )

        except Exception as e:
            print(f"Error: {e}")
            results.append(
                {
                    "test": test_case["name"],
                    "username": test_case["username"],
                    "should_show": "ERROR",
                    "error": str(e),
                }
            )

    # Summary
    print(f"\n{'=' * 50}")
    print("SUMMARY")
    print(f"{'=' * 50}")

    for result in results:
        status = (
            "✓"
            if result["should_show"] == True
            else "✗"
            if result["should_show"] == False
            else "❌"
        )
        print(f"{status} {result['test']}: {result['should_show']}")

    print(f"\nExpected Results:")
    print("✓ New User (No Company): True")
    print("✓ User with Company but No Subscription: True")
    print("✓ User with Active Trial: False")
    print("✓ User with Expired Trial: True")
    print("✓ User with Active Subscription: False")
    print("✓ Recent User (Created < 24 hours): True")
    print("✓ Trial Expiring Soon (< 7 days): True")


# Helper functions to create test scenarios
def create_new_user(username):
    user, _ = User.objects.get_or_create(
        username=username, defaults={"email": f"{username}@test.com"}
    )
    return user


def create_company_no_subscription(username):
    user = create_new_user(username)
    Company.objects.get_or_create(
        name=f"{username} Company", defaults={"email": f"{username}@company.com"}
    )
    return user


def create_active_trial(username):
    user = create_new_user(username)
    company, _ = Company.objects.get_or_create(
        name=f"{username} Company", defaults={"email": f"{username}@company.com"}
    )
    from superadmin.models import Plan

    plan = Plan.objects.filter(is_active=True).first()
    if plan:
        Subscription.objects.get_or_create(
            company=company,
            plan=plan,
            defaults={
                "status": "trial",
                "start_date": timezone.now().date(),
                "end_date": timezone.now().date() + timezone.timedelta(days=30),
                "total_amount": plan.price,
            },
        )
    return user


def create_expired_trial(username):
    user = create_new_user(username)
    company, _ = Company.objects.get_or_create(
        name=f"{username} Company", defaults={"email": f"{username}@company.com"}
    )
    from superadmin.models import Plan

    plan = Plan.objects.filter(is_active=True).first()
    if plan:
        Subscription.objects.get_or_create(
            company=company,
            plan=plan,
            defaults={
                "status": "expired",
                "start_date": timezone.now().date() - timezone.timedelta(days=40),
                "end_date": timezone.now().date() - timezone.timedelta(days=10),
                "total_amount": plan.price,
            },
        )
    return user


def create_active_subscription(username):
    user = create_new_user(username)
    company, _ = Company.objects.get_or_create(
        name=f"{username} Company", defaults={"email": f"{username}@company.com"}
    )
    from superadmin.models import Plan

    plan = Plan.objects.filter(is_active=True).first()
    if plan:
        Subscription.objects.get_or_create(
            company=company,
            plan=plan,
            defaults={
                "status": "active",
                "start_date": timezone.now().date() - timezone.timedelta(days=10),
                "end_date": timezone.now().date() + timezone.timedelta(days=20),
                "total_amount": plan.price,
            },
        )
    return user


def create_recent_user(username):
    user, created = User.objects.get_or_create(
        username=username, defaults={"email": f"{username}@test.com"}
    )
    if created:
        # Update created_at to be recent
        user.date_joined = timezone.now() - timezone.timedelta(hours=12)
        user.save()
    return user


def create_trial_expiring_soon(username):
    user = create_new_user(username)
    company, _ = Company.objects.get_or_create(
        name=f"{username} Company", defaults={"email": f"{username}@company.com"}
    )
    from superadmin.models import Plan

    plan = Plan.objects.filter(is_active=True).first()
    if plan:
        Subscription.objects.get_or_create(
            company=company,
            plan=plan,
            defaults={
                "status": "trial",
                "start_date": timezone.now().date() - timezone.timedelta(days=23),
                "end_date": timezone.now().date()
                + timezone.timedelta(days=5),  # 5 days remaining
                "total_amount": plan.price,
            },
        )
    return user


if __name__ == "__main__":
    test_all_scenarios()
