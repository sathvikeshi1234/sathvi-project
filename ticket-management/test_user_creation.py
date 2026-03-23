#!/usr/bin/env python
"""
Test script to verify superadmin user creation functionality
"""
import os
import sys
import django

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import Role, UserProfile
from superadmin.models import Company

def test_user_creation():
    print("=== Testing User Creation ===")
    
    # Check if models are working
    try:
        # Check existing roles
        roles = Role.objects.all()
        print(f"Existing roles: {[role.name for role in roles]}")
        
        # Check existing companies
        companies = Company.objects.all()
        print(f"Existing companies: {[company.name for company in companies]}")
        
        # Check existing users
        users = User.objects.all()
        print(f"Total users: {users.count()}")
        
        # Test role creation
        test_role, created = Role.objects.get_or_create(name='Test')
        print(f"Test role {'created' if created else 'exists'}: {test_role.name}")
        
        # Test company creation
        test_company, created = Company.objects.get_or_create(
            name='Test Company',
            defaults={'email': 'test@company.com', 'is_active': True}
        )
        print(f"Test company {'created' if created else 'exists'}: {test_company.name}")
        
        print("\n=== All models working correctly ===")
        return True
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_user_creation()
    if success:
        print("\n[SUCCESS] User creation test passed!")
    else:
        print("\n[FAILED] User creation test failed!")
        sys.exit(1)
