#!/usr/bin/env python3
"""
Check user status and fix inactive users
"""

import os
import sys
import django

# Add project path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.users.models import UserProfile

def check_users():
    print("Checking user status...")
    print("=" * 50)
    
    users = User.objects.all()
    
    if not users:
        print("No users found in database")
        return
    
    for user in users:
        print(f"\nUser: {user.username}")
        print(f"  Email: {user.email}")
        print(f"  Django User.is_active: {user.is_active}")
        print(f"  is_staff: {user.is_staff}")
        print(f"  is_superuser: {user.is_superuser}")
        
        # Check UserProfile
        try:
            profile = user.userprofile
            print(f"  UserProfile.is_active: {profile.is_active}")
            print(f"  Role: {profile.role}")
        except UserProfile.DoesNotExist:
            print("  No UserProfile found")
        
        print(f"  Status: {'ACTIVE' if user.is_active else 'INACTIVE'}")
    
    print("\n" + "=" * 50)

def activate_user(username):
    """Activate a specific user"""
    try:
        user = User.objects.get(username=username)
        
        # Activate Django User
        user.is_active = True
        user.save()
        
        # Activate UserProfile if exists
        try:
            profile = user.userprofile
            profile.is_active = True
            profile.save()
            print(f"✅ Activated user '{username}' and their profile")
        except UserProfile.DoesNotExist:
            print(f"✅ Activated user '{username}' (no profile found)")
            
    except User.DoesNotExist:
        print(f"❌ User '{username}' not found")

def create_test_user():
    """Create a test user for login"""
    username = "testuser"
    password = "testpass123"
    email = "testuser@example.com"
    
    # Check if user already exists
    if User.objects.filter(username=username).exists():
        print(f"User '{username}' already exists")
        return
    
    # Create user
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        is_active=True
    )
    
    # Create UserProfile
    from apps.users.models import Role
    user_role, _ = Role.objects.get_or_create(name='User')
    
    UserProfile.objects.create(
        user=user,
        role=user_role,
        is_active=True
    )
    
    print(f"✅ Created test user '{username}' with password '{password}'")

if __name__ == "__main__":
    # Check current users
    check_users()
    
    # Create test user if needed
    create_test_user()
    
    print("\nTo activate a specific user, run:")
    print("python check_user_status.py activate <username>")
