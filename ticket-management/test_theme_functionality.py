#!/usr/bin/env python3
"""
Test theme functionality end-to-end
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

def test_theme_functionality():
    print("Testing theme functionality...")
    print("=" * 50)
    
    # Test user
    username = "testlogin"
    
    try:
        user = User.objects.get(username=username)
        profile = user.userprofile
        
        print(f"User: {username}")
        print(f"Current theme in database: {profile.theme}")
        print(f"Dark mode: {profile.dark_mode}")
        
        # Test different theme values
        themes = ['light', 'dark', 'system']
        
        for theme in themes:
            print(f"\n--- Testing theme: {theme} ---")
            
            # Simulate backend update
            profile.theme = theme
            profile.dark_mode = (theme == 'dark')
            profile.save()
            
            # Reload to verify
            profile.refresh_from_db()
            print(f"Saved theme: {profile.theme}")
            print(f"Dark mode: {profile.dark_mode}")
        
        # Reset to system
        profile.theme = 'system'
        profile.dark_mode = False
        profile.save()
        
        print(f"\nReset to system theme")
        print("Theme functionality test completed successfully!")
        
    except User.DoesNotExist:
        print(f"User '{username}' not found")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_theme_functionality()
