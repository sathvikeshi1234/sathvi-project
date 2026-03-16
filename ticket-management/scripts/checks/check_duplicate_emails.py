#!/usr/bin/env python
"""
Check for duplicate emails in the database
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
from collections import defaultdict


def check_duplicate_emails():
    print("Checking for duplicate emails...")
    print("=" * 40)

    # Get all users
    users = User.objects.all()
    print(f"Total users: {users.count()}")

    # Group users by email
    email_groups = defaultdict(list)
    for user in users:
        if user.email:  # Skip empty emails
            email_groups[user.email].append(user)

    # Find duplicates
    duplicates = {
        email: users for email, users in email_groups.items() if len(users) > 1
    }

    if duplicates:
        print(f"\nFound {len(duplicates)} duplicate emails:")
        print("-" * 40)

        for email, user_list in duplicates.items():
            print(f"\nEmail: {email}")
            print(f"Count: {len(user_list)} users")
            for user in user_list:
                print(f"  - Username: {user.username}")
                print(f"    ID: {user.id}")
                print(f"    Email: {user.email}")
                print(f"    Is Staff: {user.is_staff}")
                print(f"    Is Superuser: {user.is_superuser}")
                print(f"    Created: {user.date_joined}")
                print()
    else:
        print("\nNo duplicate emails found!")

    # Show email statistics
    print(f"\nEmail Statistics:")
    print(f"Unique emails: {len(email_groups)}")
    print(f"Users with emails: {sum(len(users) for users in email_groups.values())}")
    print(f"Users without emails: {users.filter(email='').count()}")

    return duplicates


if __name__ == "__main__":
    check_duplicate_emails()
