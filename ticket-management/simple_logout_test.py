#!/usr/bin/env python3
"""
Simple test to verify logout redirects work.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.append(os.path.join(os.path.dirname(__file__), 'apps'))
django.setup()

from django.test import Client
from django.urls import reverse

def test_logout_urls():
    print("Testing Logout URL Redirects")
    print("=" * 40)
    
    client = Client()
    
    # Test logout without login (should redirect to user_login by default)
    print("\n1. Testing logout without login:")
    response = client.get(reverse('users:logout'))
    if response.status_code == 302:
        print(f"   ✅ Logout redirects to: {response.url}")
        if 'user-login' in response.url:
            print("   ✅ Correctly redirects to user-login by default")
        else:
            print(f"   ⚠️  Unexpected redirect: {response.url}")
    else:
        print(f"   ❌ Expected redirect, got status: {response.status_code}")
    
    print("\n2. Available login URLs:")
    print(f"   - Admin Login: {reverse('users:admin_login')}")
    print(f"   - Agent Login: {reverse('users:agent_login')}")
    print(f"   - User Login: {reverse('users:user_login')}")
    print(f"   - Main Login: {reverse('users:login')}")
    
    print("\n3. Logout URL:")
    print(f"   - Logout: {reverse('users:logout')}")
    
    print("\n" + "=" * 40)
    print("✅ Basic URL test completed!")
    print("\nManual Testing Instructions:")
    print("1. Start the server: python manage.py runserver")
    print("2. Open browser and test each role:")
    print("   - Admin: Go to /admin-login/, login, then logout")
    print("   - Agent: Go to /agent-login/, login, then logout") 
    print("   - User: Go to /user-login/, login, then logout")
    print("3. Verify each logout redirects to the appropriate login page")

if __name__ == '__main__':
    test_logout_urls()
