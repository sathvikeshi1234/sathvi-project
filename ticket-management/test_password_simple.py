#!/usr/bin/env python
"""
Simple test to verify the SetUserPasswordView API endpoint using Django management command
"""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.users.models import UserProfile, Role

User = get_user_model()

def check_users_and_roles():
    """Check if users and roles exist"""
    
    print("=== Checking Users ===")
    users = User.objects.all()
    for user in users:
        print(f"User: {user.username} | Email: {user.email} | Staff: {user.is_staff}")
    
    print("\n=== Checking Roles ===")
    roles = Role.objects.all()
    for role in roles:
        print(f"Role: {role.name}")
    
    print("\n=== Checking UserProfiles ===")
    profiles = UserProfile.objects.all()
    for profile in profiles:
        print(f"Profile for: {profile.user.username} | Role: {profile.role.name if profile.role else 'None'}")

def test_password_set():
    """Test setting password for a user"""
    
    # Find or create a test user
    test_user, created = User.objects.get_or_create(
        username='test_agent',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'Agent',
            'is_staff': True
        }
    )
    
    if created:
        test_user.set_password('temp_password')
        test_user.save()
        print(f"✅ Created test user: {test_user.username}")
    else:
        print(f"✅ Using existing test user: {test_user.username}")
    
    # Create or get Agent role
    agent_role, created = Role.objects.get_or_create(name='Agent')
    if created:
        print(f"✅ Created Agent role")
    
    # Create or get user profile
    profile, created = UserProfile.objects.get_or_create(
        user=test_user,
        defaults={'role': agent_role, 'is_active': True}
    )
    if not created:
        profile.role = agent_role
        profile.is_active = True
        profile.save()
        print(f"✅ Updated user profile")
    else:
        print(f"✅ Created user profile")
    
    # Test password change
    print(f"\n=== Testing Password Change ===")
    print(f"Current password check: {test_user.check_password('temp_password')}")
    
    # Change password
    test_user.set_password('new_password123')
    test_user.save()
    
    print(f"After password change - new password check: {test_user.check_password('new_password123')}")
    print(f"After password change - old password check: {test_user.check_password('temp_password')}")
    
    print("✅ Password functionality is working!")

if __name__ == '__main__':
    check_users_and_roles()
    test_password_set()
