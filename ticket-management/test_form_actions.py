#!/usr/bin/env python3
"""
Test different form actions to ensure they work correctly
"""

import os
import sys
import django

# Add project path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import UserProfile
from django.test import Client
from django.urls import reverse

def test_form_actions():
    print("Testing different form actions...")
    print("=" * 60)
    
    # Get test user
    username = "testlogin"
    
    try:
        user = User.objects.get(username=username)
        profile = user.userprofile
        
        print(f"Testing with user: {username}")
        print(f"Initial status - User.is_active: {user.is_active}, Profile.is_active: {profile.is_active}")
        
        client = Client()
        
        # Login the user
        login_success = client.login(username=username, password='test123')
        print(f"Login successful: {login_success}")
        
        # Test 1: Settings save (should NOT deactivate user)
        print(f"\n--- Test 1: Settings Save ---")
        post_data = {
            'action': 'settings',
            'theme': 'light',
            'email_notifications': 'on',
            'push_notifications': 'off',
        }
        
        response = client.post('/dashboard/user-dashboard/settings/', post_data)
        print(f"Settings save response: {response.status_code}")
        
        # Check user status after settings save
        user.refresh_from_db()
        profile.refresh_from_db()
        print(f"After settings save - User.is_active: {user.is_active}, Profile.is_active: {profile.is_active}")
        print(f"Theme saved: {profile.theme}")
        
        # Reactivate if needed
        if not user.is_active or not profile.is_active:
            user.is_active = True
            user.save()
            profile.is_active = True
            profile.save()
            print("Reactivated user for next test")
        
        # Test 2: Deactivate action (should deactivate user)
        print(f"\n--- Test 2: Deactivate Action ---")
        post_data = {
            'action': 'deactivate',
        }
        
        response = client.post('/dashboard/user-dashboard/settings/', post_data)
        print(f"Deactivate response: {response.status_code}")
        
        # Check user status after deactivate
        user.refresh_from_db()
        profile.refresh_from_db()
        print(f"After deactivate - User.is_active: {user.is_active}, Profile.is_active: {profile.is_active}")
        
        # Reactivate for next test
        user.is_active = True
        user.save()
        profile.is_active = True
        profile.save()
        print("Reactivated user for next test")
        
        # Test 3: Delete action (should deactivate user)
        print(f"\n--- Test 3: Delete Action ---")
        post_data = {
            'action': 'delete',
        }
        
        response = client.post('/dashboard/user-dashboard/settings/', post_data)
        print(f"Delete response: {response.status_code}")
        
        # Check user status after delete
        user.refresh_from_db()
        profile.refresh_from_db()
        print(f"After delete - User.is_active: {user.is_active}, Profile.is_active: {profile.is_active}")
        
        # Final reactivation
        user.is_active = True
        user.save()
        profile.is_active = True
        profile.save()
        print("Reactivated user - Test complete")
        
    except User.DoesNotExist:
        print(f"User '{username}' not found")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_form_actions()
