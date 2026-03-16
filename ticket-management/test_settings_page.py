#!/usr/bin/env python3
"""
Test script to verify settings page functionality
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User
from users.models import UserProfile

class SettingsPageTest(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create user profile
        self.profile = UserProfile.objects.create(
            user=self.user,
            dark_mode=False,
            theme='light',
            email_notifications=True,
            desktop_notifications=False
        )

    def test_settings_page_loads(self):
        """Test that settings page loads successfully"""
        # Login user
        self.client.login(username='testuser', password='testpass123')
        
        # Check settings page
        response = self.client.get('/dashboard/user-dashboard/settings/')
        
        # Should load successfully
        self.assertEqual(response.status_code, 200)
        
        # Should contain settings form
        self.assertContains(response, 'settings-form')
        self.assertContains(response, 'Settings')
        
        # Should contain user preferences
        self.assertContains(response, 'theme')
        self.assertContains(response, 'email_notifications')

    def test_settings_post_request(self):
        """Test that settings POST request works"""
        # Login user
        self.client.login(username='testuser', password='testpass123')
        
        # Post settings
        response = self.client.post('/dashboard/user-dashboard/settings/', {
            'action': 'settings',
            'theme': 'dark',
            'email_notifications': 'on',
            'push_notifications': 'off',
            'csrfmiddlewaretoken': 'test'
        })
        
        # Should redirect after successful save
        self.assertEqual(response.status_code, 302)
        
        # Check if profile was updated
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.dark_mode)
        self.assertEqual(self.profile.theme, 'dark')

if __name__ == '__main__':
    print("Testing Settings Page...")
    print("=" * 50)
    
    # Create test instance
    test = SettingsPageTest()
    test.setUp()
    
    try:
        print("1. Testing settings page loads...")
        test.test_settings_page_loads()
        print("✓ PASS: Settings page loads successfully")
        
        print("\n2. Testing settings POST request...")
        test.test_settings_post_request()
        print("✓ PASS: Settings POST request works")
        
        print("\n" + "=" * 50)
        print("🎉 ALL TESTS PASSED! Settings page is working correctly.")
        
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        print("\nPlease check the implementation and try again.")
