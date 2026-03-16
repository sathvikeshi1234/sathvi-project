#!/usr/bin/env python3
"""
Simple test to check URL routing without Unicode
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User

def test_url_routing():
    print("Testing URL Routing...")
    print("=" * 50)
    
    # Test URL reverse
    try:
        url = reverse('dashboards:user_dashboard_page', kwargs={'page': 'settings'})
        print(f"URL reverse successful: {url}")
    except Exception as e:
        print(f"URL reverse failed: {e}")
        return
    
    # Test direct URL access
    client = Client()
    
    # Try without authentication
    print("\n1. Testing without authentication...")
    response = client.get(url)
    print(f"   Status: {response.status_code}")
    if response.status_code == 302:
        print(f"   Redirect to: {response.url}")
    
    # Create a test user and authenticate
    print("\n2. Creating test user...")
    try:
        user = User.objects.create_user(
            username='testuser456',
            email='test456@example.com',
            password='testpass123'
        )
        print(f"   User created: {user.username}")
    except Exception as e:
        print(f"   User creation failed: {e}")
        # Try to get existing user
        try:
            user = User.objects.get(username='testuser456')
            print(f"   Using existing user: {user.username}")
        except:
            print("   No test user available")
            return
    
    # Test with authentication
    print("\n3. Testing with authentication...")
    client.force_login(user)
    response = client.get(url)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print("   SUCCESS: Settings page accessible!")
        content = response.content.decode('utf-8')
        
        # Check for key elements
        if 'Settings' in content:
            print("   Settings title found")
        if 'settings-form' in content:
            print("   Settings form found")
        if 'theme' in content:
            print("   Theme controls found")
        if 'dark_mode' in content:
            print("   Dark mode variable found")
    else:
        print(f"   FAILED: {response.status_code}")
        if hasattr(response, 'content'):
            print(f"   Content preview: {response.content[:200]}...")

if __name__ == '__main__':
    test_url_routing()
