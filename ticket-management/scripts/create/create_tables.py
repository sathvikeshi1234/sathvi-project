import os
import sys
from pathlib import Path
import django

# Set up Django environment
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mainproject.settings")
django.setup()

from django.db import connection

# Create core_plan table manually
with connection.cursor() as cursor:
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS core_plan (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100) UNIQUE NOT NULL,
        slug VARCHAR(120) UNIQUE NOT NULL,
        description TEXT NOT NULL,
        plan_type VARCHAR(20) NOT NULL,
        price_monthly DECIMAL(10,2) NOT NULL,
        price_quarterly DECIMAL(10,2) NULL,
        price_annually DECIMAL(10,2) NULL,
        price_biennial DECIMAL(10,2) NULL,
        currency VARCHAR(3) NOT NULL DEFAULT 'USD',
        billing_cycles VARCHAR(20) NOT NULL DEFAULT 'monthly',
        trial_days INTEGER NOT NULL DEFAULT 0,
        trial_features TEXT NOT NULL DEFAULT '{}',
        max_users INTEGER NULL,
        max_tickets_per_month INTEGER NULL,
        max_agents INTEGER NULL,
        storage_limit_gb INTEGER NULL,
        api_calls_per_month INTEGER NULL,
        features TEXT NOT NULL DEFAULT '{}',
        status VARCHAR(20) NOT NULL DEFAULT 'draft',
        is_popular BOOLEAN NOT NULL DEFAULT 0,
        sort_order INTEGER NOT NULL DEFAULT 0,
        created_at DATETIME NOT NULL,
        updated_at DATETIME NOT NULL,
        metadata TEXT NOT NULL DEFAULT '{}'
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS core_subscription (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL UNIQUE,
        plan_id INTEGER NULL,
        status VARCHAR(20) NOT NULL DEFAULT 'unpaid',
        current_period_start DATETIME NULL,
        current_period_end DATETIME NULL,
        trial_start DATETIME NULL,
        trial_end DATETIME NULL,
        amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
        currency VARCHAR(3) NOT NULL DEFAULT 'USD',
        stripe_subscription_id VARCHAR(100) NULL,
        metadata TEXT NOT NULL DEFAULT '{}',
        created_at DATETIME NOT NULL,
        updated_at DATETIME NOT NULL,
        FOREIGN KEY (user_id) REFERENCES auth_user(id),
        FOREIGN KEY (plan_id) REFERENCES core_plan(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS core_payment (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        subscription_id INTEGER NULL,
        amount DECIMAL(10,2) NOT NULL,
        currency VARCHAR(3) NOT NULL DEFAULT 'USD',
        status VARCHAR(20) NOT NULL DEFAULT 'pending',
        stripe_payment_intent_id VARCHAR(100) NULL,
        payment_method VARCHAR(50) NOT NULL,
        created_at DATETIME NOT NULL,
        updated_at DATETIME NOT NULL,
        FOREIGN KEY (user_id) REFERENCES auth_user(id),
        FOREIGN KEY (subscription_id) REFERENCES core_subscription(id)
    );
    """)

print("Core tables created successfully!")
