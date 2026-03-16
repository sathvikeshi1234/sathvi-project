#!/usr/bin/env python
"""
Expire a user's trial to test payment modal
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
from django.utils import timezone
from superadmin.views import check_subscription_expiry


def expire_user_trial(username):
    print(f"Expiring trial for user: {username}")
    print("=" * 40)

    # Get user
    try:
        user = User.objects.get(username=username)
        print(f"Found user: {user.username}")
    except User.DoesNotExist:
        print(f"User {username} not found")
        return

    # Get company
    company_name = f"{username} Company"
    company = Company.objects.filter(name=company_name).first()

    if not company:
        print(f"Company {company_name} not found")
        return

    print(f"Found company: {company.name}")

    # Get subscription
    subscription = company.subscriptions.first()

    if not subscription:
        print(f"No subscription found for {company_name}")
        return

    print(f"Current subscription: {subscription.id}")
    print(f"Current status: {subscription.status}")
    print(f"Current end_date: {subscription.end_date}")

    # Expire the trial
    subscription.status = "expired"
    subscription.end_date = timezone.now().date() - timezone.timedelta(
        days=1
    )  # Yesterday
    subscription.save()

    print(f"\nUpdated subscription:")
    print(f"New status: {subscription.status}")
    print(f"New end_date: {subscription.end_date}")

    # Test check_subscription_expiry
    result = check_subscription_expiry(user)
    print(f"\ncheck_subscription_expiry result: {result}")
    print(f"Should show modal: {result}")

    if result:
        print(f"\nSUCCESS! Payment modal should now show for user {username}")
        print(f"Test URL: http://localhost:8000/dashboard/admin-dashboard/")
    else:
        print(f"\nFAILED! Payment modal still won't show")


if __name__ == "__main__":
    # Expire trial for a test user
    expire_user_trial("sai")  # Change this to any username you want to test
