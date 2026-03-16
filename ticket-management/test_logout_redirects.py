#!/usr/bin/env python3
"""
Test script to verify role-based logout redirects.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.append(os.path.join(os.path.dirname(__file__), 'apps'))
django.setup()

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from apps.users.models import UserProfile, Role

User = get_user_model()

def test_logout_redirects():
    print("Testing Role-Based Logout Redirects")
    print("=" * 50)
    
    # Create test roles
    admin_role, _ = Role.objects.get_or_create(name='Admin')
    agent_role, _ = Role.objects.get_or_create(name='Agent')
    user_role, _ = Role.objects.get_or_create(name='User')
    
    # Create test users
    admin_user = User.objects.create_user(
        username='admin_test',
        email='admin@test.com',
        password='testpass123'
    )
    admin_profile, _ = UserProfile.objects.get_or_create(user=admin_user)
    admin_profile.role = admin_role
    admin_profile.save()
    
    agent_user = User.objects.create_user(
        username='agent_test',
        email='agent@test.com',
        password='testpass123'
    )
    agent_profile, _ = UserProfile.objects.get_or_create(user=agent_user)
    agent_profile.role = agent_role
    agent_profile.save()
    
    regular_user = User.objects.create_user(
        username='user_test',
        email='user@test.com',
        password='testpass123'
    )
    user_profile, _ = UserProfile.objects.get_or_create(user=regular_user)
    user_profile.role = user_role
    user_profile.save()
    
    client = Client()
    
    # Test admin logout redirect
    print("\n1. Testing Admin Logout Redirect:")
    client.login(username='admin_test', password='testpass123')
    response = client.get(reverse('users:logout'))
    expected_redirect = reverse('users:admin_login')
    if response.status_code == 302 and expected_redirect in response.url:
        print("   ✅ Admin logout redirects to admin-login")
    else:
        print(f"   ❌ Admin logout failed. Expected: {expected_redirect}, Got: {response.url}")
    
    # Test agent logout redirect
    print("\n2. Testing Agent Logout Redirect:")
    client.login(username='agent_test', password='testpass123')
    response = client.get(reverse('users:logout'))
    expected_redirect = reverse('users:agent_login')
    if response.status_code == 302 and expected_redirect in response.url:
        print("   ✅ Agent logout redirects to agent-login")
    else:
        print(f"   ❌ Agent logout failed. Expected: {expected_redirect}, Got: {response.url}")
    
    # Test regular user logout redirect
    print("\n3. Testing User Logout Redirect:")
    client.login(username='user_test', password='testpass123')
    response = client.get(reverse('users:logout'))
    expected_redirect = reverse('users:user_login')
    if response.status_code == 302 and expected_redirect in response.url:
        print("   ✅ User logout redirects to user-login")
    else:
        print(f"   ❌ User logout failed. Expected: {expected_redirect}, Got: {response.url}")
    
    # Test logout without login (should still work)
    print("\n4. Testing Logout Without Login:")
    client.logout()
    response = client.get(reverse('users:logout'))
    expected_redirect = reverse('users:user_login')  # Default to user login
    if response.status_code == 302 and expected_redirect in response.url:
        print("   ✅ Logout without login redirects to user-login")
    else:
        print(f"   ❌ Logout without login failed. Expected: {expected_redirect}, Got: {response.url}")
    
    print("\n" + "=" * 50)
    print("✅ Role-based logout redirect tests completed!")
    
    # Clean up test data
    admin_user.delete()
    agent_user.delete()
    regular_user.delete()
    
    print("\nManual Testing Steps:")
    print("1. Login as admin at /admin-login/")
    print("2. Click logout - should redirect to /admin-login/")
    print("3. Login as agent at /agent-login/")
    print("4. Click logout - should redirect to /agent-login/")
    print("5. Login as regular user at /user-login/")
    print("6. Click logout - should redirect to /user-login/")

if __name__ == '__main__':
    test_logout_redirects()
