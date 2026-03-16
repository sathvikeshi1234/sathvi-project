"""
Script to create sample plans for testing the payment system
"""

import os
import sys
from pathlib import Path
import django

# Set up Django environment
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mainproject.settings")
django.setup()

from core.models import Plan


def create_sample_plans():
    """Create sample subscription plans"""

    plans_data = [
        {
            "name": "Free",
            "description": "Perfect for individuals and small projects",
            "plan_type": "basic",
            "price_monthly": 0,
            "trial_days": 0,
            "max_tickets_per_month": 10,
            "max_agents": 1,
            "storage_limit_gb": 1,
            "api_calls_per_month": 100,
            "features": {
                "basic_support": True,
                "email_notifications": True,
                "dashboard_access": True,
                "basic_analytics": True,
            },
            "status": "active",
            "sort_order": 1,
        },
        {
            "name": "Professional",
            "description": "Great for growing teams and businesses",
            "plan_type": "standard",
            "price_monthly": 29,
            "trial_days": 14,
            "max_tickets_per_month": 100,
            "max_agents": 5,
            "storage_limit_gb": 10,
            "api_calls_per_month": 1000,
            "features": {
                "basic_support": True,
                "email_notifications": True,
                "dashboard_access": True,
                "basic_analytics": True,
                "priority_support": True,
                "custom_integrations": True,
                "advanced_analytics": True,
            },
            "status": "active",
            "sort_order": 2,
            "is_popular": True,
        },
        {
            "name": "Business",
            "description": "Complete solution for large organizations",
            "plan_type": "premium",
            "price_monthly": 99,
            "trial_days": 30,
            "max_tickets_per_month": 1000,
            "max_agents": 20,
            "storage_limit_gb": 100,
            "api_calls_per_month": 10000,
            "features": {
                "basic_support": True,
                "email_notifications": True,
                "dashboard_access": True,
                "basic_analytics": True,
                "priority_support": True,
                "custom_integrations": True,
                "advanced_analytics": True,
                "dedicated_support": True,
                "custom_branding": True,
                "sla_guarantee": True,
            },
            "status": "active",
            "sort_order": 3,
        },
        {
            "name": "Enterprise",
            "description": "Tailored solutions for enterprise needs",
            "plan_type": "enterprise",
            "price_monthly": 299,
            "trial_days": 30,
            "max_tickets_per_month": None,  # unlimited
            "max_agents": None,  # unlimited
            "storage_limit_gb": None,  # unlimited
            "api_calls_per_month": None,  # unlimited
            "features": {
                "basic_support": True,
                "email_notifications": True,
                "dashboard_access": True,
                "basic_analytics": True,
                "priority_support": True,
                "custom_integrations": True,
                "advanced_analytics": True,
                "dedicated_support": True,
                "custom_branding": True,
                "sla_guarantee": True,
                "on_premise_deployment": True,
                "custom_training": True,
                "account_manager": True,
            },
            "status": "active",
            "sort_order": 4,
        },
    ]

    created_plans = []
    for plan_data in plans_data:
        plan, created = Plan.objects.get_or_create(
            name=plan_data["name"], defaults=plan_data
        )
        if created:
            print(f"Created plan: {plan.name}")
            created_plans.append(plan)
        else:
            print(f"Plan already exists: {plan.name}")
            # Update existing plan with new data
            for key, value in plan_data.items():
                if key != "name":  # Don't update the name
                    setattr(plan, key, value)
            plan.save()
            print(f"Updated plan: {plan.name}")

    print(f"\nTotal plans in database: {Plan.objects.count()}")
    print("Available plans:")
    for plan in Plan.objects.filter(status="active").order_by("sort_order"):
        print(f"- {plan.name}: ${plan.get_display_price('monthly')}/month")
        if plan.is_popular:
            print("  (POPULAR)")

    return created_plans


if __name__ == "__main__":
    print("Creating sample plans...")
    create_sample_plans()
    print("Done!")
