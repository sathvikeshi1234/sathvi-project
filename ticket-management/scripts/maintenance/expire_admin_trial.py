#!/usr/bin/env python
"""
Expire admin user's trial to test payment modal
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


def expire_admin_trial(username):
    print(f"Expiring trial for admin user: {username}")
    print("=" * 40)

    # Get user
    try:
        user = User.objects.get(username=username)
        print(f"User found: {user.username}")
    except User.DoesNotExist:
        print(f"User {username} not found")
        return

    # Get company
    expected_company = f"{username} Company"
    company = Company.objects.filter(name=expected_company).first()

    if not company:
        print(f"Company {expected_company} not found")
        return

    print(f"Found company: {company.name}")

    # Get latest subscription
    subscription = company.subscriptions.order_by("-created_at").first()

    if not subscription:
        print(f"No subscription found")
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
        print(f"Test URL: http://localhost:8003/dashboard/admin-dashboard/")
    else:
        print(f"\nFAILED! Payment modal still won't show")


if __name__ == "__main__":
    expire_admin_trial("sathvika.arikatla")  # Change this to your admin username
