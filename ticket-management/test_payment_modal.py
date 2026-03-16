#!/usr/bin/env python
"""
Test script to verify payment modal shows for new users
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import UserProfile, Role
from superadmin.views import should_show_payment_modal

def test_payment_modal_for_new_user():
    """Test that new users see the payment modal"""
    print("Testing Payment Modal for New Users...")
    
    # Create test role
    user_role, _ = Role.objects.get_or_create(name='User')
    
    # Create test user (not staff, not superuser)
    test_user, _ = User.objects.get_or_create(
        username='test_new_user', 
        defaults={
            'email': 'newuser@test.com',
            'is_staff': False,
            'is_superuser': False
        }
    )
    
    # Create user profile with User role
    profile, created = UserProfile.objects.get_or_create(
        user=test_user, 
        defaults={'role': user_role}
    )
    if not created:
        profile.role = user_role
        profile.save()
    
    print(f"Test user: {test_user.username}")
    print(f"Is staff: {test_user.is_staff}")
    print(f"Is superuser: {test_user.is_superuser}")
    print(f"Role: {test_user.userprofile.role.name}")
    
    # Test if payment modal should show
    should_show = should_show_payment_modal(test_user)
    
    print(f"\nShould show payment modal: {should_show}")
    
    if should_show:
        print("SUCCESS: New user will see payment modal")
    else:
        print("ISSUE: New user will NOT see payment modal")
    
    return should_show

if __name__ == '__main__':
    success = test_payment_modal_for_new_user()
    sys.exit(0 if success else 1)
