#!/usr/bin/env python
"""
Security Test Script to verify role-based access control
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User
from users.models import UserProfile, Role
from django.urls import reverse

def test_role_access_control():
    """Test that users cannot access dashboards outside their role"""
    print("Testing Role-Based Access Control...")
    
    # Create test roles
    admin_role, _ = Role.objects.get_or_create(name='Admin')
    agent_role, _ = Role.objects.get_or_create(name='Agent')
    user_role, _ = Role.objects.get_or_create(name='User')
    
    # Create test users
    admin_user, _ = User.objects.get_or_create(username='test_admin', defaults={'is_staff': True})
    agent_user, _ = User.objects.get_or_create(username='test_agent', defaults={'is_staff': True})
    regular_user, _ = User.objects.get_or_create(username='test_user')
    
    # Create or update user profiles with correct roles
    admin_profile, created = UserProfile.objects.get_or_create(user=admin_user, defaults={'role': admin_role})
    if not created:
        admin_profile.role = admin_role
        admin_profile.save()
        
    agent_profile, created = UserProfile.objects.get_or_create(user=agent_user, defaults={'role': agent_role})
    if not created:
        agent_profile.role = agent_role
        agent_profile.save()
        
    user_profile, created = UserProfile.objects.get_or_create(user=regular_user, defaults={'role': user_role})
    if not created:
        user_profile.role = user_role
        user_profile.save()
    
    # Verify roles are set correctly
    print(f"User roles: {admin_user.username} -> {admin_user.userprofile.role.name}, {agent_user.username} -> {agent_user.userprofile.role.name}, {regular_user.username} -> {regular_user.userprofile.role.name}")
    
    client = Client()
    
    # Test cases: (user, url, expected_redirect)
    test_cases = [
        # Agent trying to access admin pages
        (agent_user, '/dashboard/admin-dashboard/reports.html', '/dashboard/agent-dashboard/'),
        (agent_user, '/dashboard/admin-dashboard/', '/dashboard/agent-dashboard/'),
        (agent_user, '/dashboard/admin-dashboard/payment/', '/dashboard/agent-dashboard/'),
        
        # Regular user trying to access admin pages
        (regular_user, '/dashboard/admin-dashboard/reports.html', '/dashboard/user-dashboard/'),
        (regular_user, '/dashboard/admin-dashboard/', '/dashboard/user-dashboard/'),
        
        # Admin trying to access agent pages
        (admin_user, '/dashboard/agent-dashboard/reports.html', '/dashboard/admin-dashboard/'),
        (admin_user, '/dashboard/agent-dashboard/', '/dashboard/admin-dashboard/'),
        
        # Regular user trying to access agent pages
        (regular_user, '/dashboard/agent-dashboard/reports.html', '/dashboard/user-dashboard/'),
        (regular_user, '/dashboard/agent-dashboard/', '/dashboard/user-dashboard/'),
        
        # Agent trying to access user pages
        (agent_user, '/dashboard/user-dashboard/reports.html', '/dashboard/agent-dashboard/'),
        (agent_user, '/dashboard/user-dashboard/', '/dashboard/agent-dashboard/'),
    ]
    
    results = []
    for test_user, test_url, expected_redirect in test_cases:
        client.force_login(test_user)
        response = client.get(test_url, follow=False)
        
        # Check if redirected to expected location
        if response.status_code == 302:
            actual_redirect = response.url
            success = expected_redirect in actual_redirect
        elif response.status_code == 301:
            # Handle permanent redirects
            follow_response = client.get(test_url, follow=True)
            if follow_response.status_code == 302:
                actual_redirect = follow_response.redirect_chain[-1][0]
                success = expected_redirect in actual_redirect
            else:
                success = False
                actual_redirect = f"Status {follow_response.status_code}"
        else:
            success = False
            actual_redirect = f"Status {response.status_code}"
        
        results.append({
            'user': test_user.username,
            'role': test_user.userprofile.role.name,
            'url': test_url,
            'expected': expected_redirect,
            'actual': actual_redirect,
            'success': success
        })
    
    # Print results
    print("\nTest Results:")
    print("=" * 80)
    
    passed = 0
    total = len(results)
    
    for result in results:
        status = "PASS" if result['success'] else "FAIL"
        print(f"{status} {result['user']} ({result['role']}) -> {result['url']}")
        if not result['success']:
            print(f"   Expected: {result['expected']}")
            print(f"   Actual: {result['actual']}")
        if result['success']:
            passed += 1
    
    print("\n" + "=" * 80)
    print(f"Summary: {passed}/{total} tests passed")
    
    if passed == total:
        print("All security tests passed! Role-based access control is working correctly.")
    else:
        print("Some security tests failed. Please review the access control implementation.")
    
    return passed == total

if __name__ == '__main__':
    success = test_role_access_control()
    sys.exit(0 if success else 1)
