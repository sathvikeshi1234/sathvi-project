#!/usr/bin/env python3
"""
Test theme save with browser simulation to identify logout issue
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
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware

def test_theme_save_browser():
    print("Testing theme save with browser simulation...")
    print("=" * 60)
    
    # Get test user
    username = "testlogin"
    
    try:
        user = User.objects.get(username=username)
        profile = user.userprofile
        
        print(f"User: {username}")
        print(f"Current theme: {profile.theme}")
        print(f"User.is_active: {user.is_active}")
        print(f"Profile.is_active: {profile.is_active}")
        
        # Create client with proper middleware simulation
        client = Client()
        
        # Step 1: Login
        print(f"\n--- Step 1: Login ---")
        login_success = client.login(username=username, password='test123')
        print(f"Login successful: {login_success}")
        
        # Step 2: Access settings page
        print(f"\n--- Step 2: Access Settings Page ---")
        response = client.get('/dashboard/user-dashboard/settings/')
        print(f"Settings page status: {response.status_code}")
        
        if response.status_code == 200:
            print("Settings page loaded successfully")
        elif response.status_code == 302:
            print("Redirected - user might not be logged in")
            print(f"Redirect to: {response.get('Location', 'Unknown')}")
        else:
            print(f"Unexpected status: {response.status_code}")
        
        # Step 3: Save theme settings
        print(f"\n--- Step 3: Save Theme Settings ---")
        post_data = {
            'action': 'settings',
            'theme': 'light',
            'email_notifications': 'on',
            'push_notifications': 'off',
        }
        
        response = client.post('/dashboard/user-dashboard/settings/', post_data)
        print(f"POST response status: {response.status_code}")
        
        if response.status_code == 302:
            print("Redirect occurred (expected)")
            print(f"Redirect to: {response.get('Location', 'Unknown')}")
        elif response.status_code == 200:
            print("Settings page rendered again")
        else:
            print(f"Unexpected status: {response.status_code}")
        
        # Step 4: Check if still logged in
        print(f"\n--- Step 4: Check Login Status ---")
        response = client.get('/dashboard/user-dashboard/settings/')
        print(f"Follow-up request status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ User still logged in - NO ISSUE")
        elif response.status_code == 302:
            print("❌ User logged out - ISSUE CONFIRMED")
            print(f"Redirect to: {response.get('Location', 'Unknown')}")
        
        # Step 5: Check database
        print(f"\n--- Step 5: Check Database ---")
        user.refresh_from_db()
        profile.refresh_from_db()
        
        print(f"User.is_active: {user.is_active}")
        print(f"Profile.is_active: {profile.is_active}")
        print(f"Theme saved: {profile.theme}")
        
        # Step 6: Check session data
        print(f"\n--- Step 6: Check Session ---")
        session = client.session
        print(f"Session exists: {bool(session.items())}")
        if session.items():
            for key, value in session.items():
                if key not in ['password', 'secret']:  # Skip sensitive data
                    print(f"  {key}: {value}")
        
    except User.DoesNotExist:
        print(f"User '{username}' not found")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_theme_save_browser()
