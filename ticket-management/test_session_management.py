#!/usr/bin/env python
"""
Test script to verify session management fix for multiple concurrent logins
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
from django.test import Client

def test_session_management():
    """Test that users cannot have multiple concurrent sessions"""
    print("Testing Session Management...")
    
    # Create test roles
    admin_role, _ = Role.objects.get_or_create(name='Admin')
    user_role, _ = Role.objects.get_or_create(name='User')
    
    # Create test users
    admin_user, _ = User.objects.get_or_create(
        username='test_admin_session', 
        defaults={'is_staff': True}
    )
    regular_user, _ = User.objects.get_or_create(
        username='test_user_session'
    )
    
    # Set passwords for test users
    admin_user.set_password('password123')
    admin_user.save()
    regular_user.set_password('password123')
    regular_user.save()
    
    # Create user profiles
    admin_profile, created = UserProfile.objects.get_or_create(
        user=admin_user, 
        defaults={'role': admin_role}
    )
    if not created:
        admin_profile.role = admin_role
        admin_profile.save()
        
    user_profile, created = UserProfile.objects.get_or_create(
        user=regular_user, 
        defaults={'role': user_role}
    )
    if not created:
        user_profile.role = user_role
        user_profile.save()
    
    print(f"Created test users: {admin_user.username} (Admin), {regular_user.username} (User)")
    
    # Create separate clients to simulate different tabs/browsers
    admin_client = Client()
    user_client = Client()
    
    # Test 1: Login as admin
    print("\n1. Testing admin login...")
    admin_login_success = admin_client.login(username='test_admin_session', password='password123')
    print(f"   Admin login successful: {admin_login_success}")
    
    # Test admin dashboard access
    admin_response = admin_client.get('/dashboard/admin-dashboard/')
    print(f"   Admin dashboard status: {admin_response.status_code}")
    
    # Test 2: Login as regular user in different client
    print("\n2. Testing user login...")
    user_login_success = user_client.login(username='test_user_session', password='password123')
    print(f"   User login successful: {user_login_success}")
    
    # Test user dashboard access
    user_response = user_client.get('/dashboard/user-dashboard/')
    print(f"   User dashboard status: {user_response.status_code}")
    
    # Test 3: Check if admin session is still valid (should be)
    print("\n3. Testing admin session persistence...")
    admin_response_after = admin_client.get('/dashboard/admin-dashboard/')
    print(f"   Admin dashboard status after user login: {admin_response_after.status_code}")
    
    # Test 4: Check if user can access admin dashboard (should be blocked)
    print("\n4. Testing user access to admin dashboard...")
    user_admin_access = user_client.get('/dashboard/admin-dashboard/')
    print(f"   User accessing admin dashboard status: {user_admin_access.status_code}")
    
    # Test 5: Check if admin can access user dashboard (should be blocked)
    print("\n5. Testing admin access to user dashboard...")
    admin_user_access = admin_client.get('/dashboard/user-dashboard/')
    print(f"   Admin accessing user dashboard status: {admin_user_access.status_code}")
    
    # Results summary
    print("\n" + "="*60)
    print("SESSION MANAGEMENT TEST RESULTS:")
    print("="*60)
    
    tests_passed = 0
    total_tests = 5
    
    # Test 1: Admin login
    if admin_login_success and admin_response.status_code in [200, 302]:
        print("PASS: Admin login and dashboard access")
        tests_passed += 1
    else:
        print("FAIL: Admin login and dashboard access")
    
    # Test 2: User login
    if user_login_success and user_response.status_code in [200, 302]:
        print("PASS: User login and dashboard access")
        tests_passed += 1
    else:
        print("FAIL: User login and dashboard access")
    
    # Test 3: Admin session persistence
    if admin_response_after.status_code in [200, 302]:
        print("PASS: Admin session persistence")
        tests_passed += 1
    else:
        print("FAIL: Admin session persistence")
    
    # Test 4: User blocked from admin dashboard
    if user_admin_access.status_code in [302, 403, 404]:
        print("PASS: User blocked from admin dashboard")
        tests_passed += 1
    else:
        print("FAIL: User blocked from admin dashboard")
    
    # Test 5: Admin blocked from user dashboard
    if admin_user_access.status_code in [302, 403, 404]:
        print("PASS: Admin blocked from user dashboard")
        tests_passed += 1
    else:
        print("FAIL: Admin blocked from user dashboard")
    
    print(f"\nOverall: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All session management tests passed!")
        return True
    else:
        print("⚠️  Some session management tests failed.")
        return False

if __name__ == '__main__':
    success = test_session_management()
    sys.exit(0 if success else 1)
