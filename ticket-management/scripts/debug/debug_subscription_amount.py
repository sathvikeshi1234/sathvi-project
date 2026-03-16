#!/usr/bin/env python
"""
Debug why subscription amounts are $0.00
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


def debug_subscription_amounts():
    print("Debugging Subscription Amounts")
    print("=" * 40)

    # Check all plans and their prices
    plans = Plan.objects.all()
    print(f"Available Plans:")
    for plan in plans:
        print(f"  - {plan.name}: ${plan.price} (Active: {plan.is_active})")

    # Check recent subscriptions
    subscriptions = Subscription.objects.all().order_by("-created_at")[:5]
    print(f"\nRecent Subscriptions:")
    for sub in subscriptions:
        print(f"  Subscription #{sub.id}:")
        print(f"    Company: {sub.company.name}")
        print(f"    Plan: {sub.plan.name}")
        print(f"    Plan Price: ${sub.plan.price}")
        print(f"    Base Price: ${sub.base_price}")
        print(f"    Discount: ${sub.discount_amount}")
        print(f"    Tax: ${sub.tax_amount}")
        print(f"    Total Amount: ${sub.total_amount}")
        print(f"    Status: {sub.status}")
        print(f"    Created: {sub.created_at}")
        print()

    # Check payments with $0.00 amount
    zero_payments = Payment.objects.filter(amount=0.00).order_by("-payment_date")[:5]
    print(f"Payments with $0.00 amount:")
    for payment in zero_payments:
        print(f"  Payment #{payment.id}:")
        print(f"    Transaction ID: {payment.transaction_id}")
        print(f"    Company: {payment.company.name}")
        print(f"    Amount: ${payment.amount}")
        print(
            f"    Subscription ID: {payment.subscription.id if payment.subscription else 'None'}"
        )
        if payment.subscription:
            sub = payment.subscription
            print(f"    Subscription Total Amount: ${sub.total_amount}")
            print(f"    Subscription Plan Price: ${sub.plan.price}")
        print(f"    Payment Date: {payment.payment_date}")
        print()

    # Find the issue: check if subscription total_amount is being set correctly
    print("Diagnosing the Issue:")
    print("-" * 30)

    # Check a specific user's subscription
    username = "sathvika.arikatla"  # Change this to test different users
    try:
        user = User.objects.get(username=username)
        company_name = f"{username} Company"
        company = Company.objects.filter(name=company_name).first()

        if company:
            subscription = company.subscriptions.order_by("-created_at").first()
            if subscription:
                print(f"User: {username}")
                print(f"Company: {company.name}")
                print(f"Subscription: #{subscription.id}")
                print(
                    f"Plan: {subscription.plan.name} (Price: ${subscription.plan.price})"
                )
                print(f"Subscription Total Amount: ${subscription.total_amount}")
                print(f"Subscription Base Price: ${subscription.base_price}")

                # Check if this is the problem
                if subscription.total_amount == 0:
                    print("PROBLEM FOUND: Subscription total_amount is 0!")
                    print("This needs to be fixed to show correct payment amount.")

                    # Fix the subscription amount
                    subscription.base_price = subscription.plan.price
                    subscription.discount_amount = 0.00
                    subscription.tax_amount = 0.00
                    subscription.total_amount = subscription.plan.price
                    subscription.save()

                    print(f"Fixed subscription amount to: ${subscription.total_amount}")
                else:
                    print("Subscription amount looks correct.")
            else:
                print("No subscription found for this user")
        else:
            print("No company found for this user")

    except User.DoesNotExist:
        print(f"User {username} not found")


if __name__ == "__main__":
    debug_subscription_amounts()
