#!/usr/bin/env python3
"""
Test settings save process to debug logout issue
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

def test_settings_save():
    print("Testing settings save process...")
    print("=" * 50)
    
    # Get test user
    username = "testlogin"
    
    try:
        user = User.objects.get(username=username)
        profile = user.userprofile
        
        print(f"User: {username}")
        print(f"Current theme: {profile.theme}")
        print(f"User.is_active: {user.is_active}")
        print(f"Profile.is_active: {profile.is_active}")
        
        # Simulate POST request to save settings
        client = Client()
        
        # Login the user
        client.force_login(user)
        
        # Test settings save POST data
        post_data = {
            'csrfmiddlewaretoken': 'test',  # We'll disable CSRF for this test
            'action': 'settings',
            'theme': 'light',
            'email_notifications': 'on',
            'push_notifications': 'off',
        }
        
        print(f"\nSimulating POST to save settings...")
        print(f"POST data: {post_data}")
        
        # Test the settings save endpoint
        try:
            from django.conf import settings
            settings.CSRF_USE_SESSIONS = False  # Disable CSRF for testing
            
            response = client.post('/dashboard/user-dashboard/settings/', post_data)
            
            print(f"Response status: {response.status_code}")
            print(f"Response location: {response.get('Location', 'None')}")
            
            if response.status_code == 302:
                print("Redirect occurred (expected)")
            elif response.status_code == 200:
                print("Settings page rendered again")
            
            # Check if user is still logged in
            if response.client and hasattr(response.client, 'session'):
                print("Session still exists")
            else:
                print("Session lost - this is the issue!")
                
        except Exception as e:
            print(f"Error during POST: {e}")
        
        # Check user status after save
        user.refresh_from_db()
        profile.refresh_from_db()
        
        print(f"\nAfter save:")
        print(f"User.is_active: {user.is_active}")
        print(f"Profile.is_active: {profile.is_active}")
        print(f"Theme: {profile.theme}")
        
    except User.DoesNotExist:
        print(f"User '{username}' not found")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_settings_save()
