#!/usr/bin/env python
"""
Create company and subscription for admin user
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
from superadmin.models import Company, Subscription, Plan
from django.utils import timezone


def create_admin_company(username):
    print(f"Creating company for admin user: {username}")
    print("=" * 40)

    # Get user
    try:
        user = User.objects.get(username=username)
        print(f"User found: {user.username}")
    except User.DoesNotExist:
        print(f"User {username} not found")
        return

    # Check if company already exists
    expected_company_name = f"{username} Company"
    existing_company = Company.objects.filter(name=expected_company_name).first()

    if existing_company:
        print(f"Company already exists: {existing_company.name}")
        subscriptions = existing_company.subscriptions.all()
        print(f"Existing subscriptions: {subscriptions.count()}")
        for sub in subscriptions:
            print(f"  - {sub.id}: {sub.status}")
        return

    # Create company
    try:
        company = Company.objects.create(
            name=expected_company_name,
            email=f"{username}@company.com",
            phone="0000000000",
            subscription_status="trial",
            subscription_start_date=timezone.now().date(),
            plan_expiry_date=timezone.now().date() + timezone.timedelta(days=30),
        )
        print(f"Created company: {company.name}")
    except Exception as e:
        print(f"Error creating company: {e}")
        return

    # Get default plan
    default_plan = Plan.objects.filter(is_active=True).first()
    if not default_plan:
        print("No active plan found")
        return

    print(f"Using plan: {default_plan.name} (Price: {default_plan.price})")

    # Create subscription
    try:
        subscription = Subscription.objects.create(
            company=company,
            plan=default_plan,
            status="trial",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=30),
            next_billing_date=timezone.now().date() + timezone.timedelta(days=30),
            base_price=default_plan.price,
            discount_amount=0.00,
            tax_amount=0.00,
            total_amount=default_plan.price,
            auto_renew=True,
        )
        print(f"Created subscription: {subscription.id}")
        print(f"Status: {subscription.status}")
        print(f"End date: {subscription.end_date}")
        print(f"Amount: {subscription.total_amount}")
    except Exception as e:
        print(f"Error creating subscription: {e}")
        return

    print(f"\nSuccess! Company and subscription created for {username}")
    print(f"Test URL: http://localhost:8003/dashboard/admin-dashboard/")
    print(
        f"Force Modal: http://localhost:8003/dashboard/admin-dashboard/?show_payment_modal=true"
    )


if __name__ == "__main__":
    create_admin_company("sathvika.arikatla")  # Change this to your admin username
