#!/usr/bin/env python3
"""
Test script to access settings page and see debug output
"""

import requests
import time

def test_settings_page():
    base_url = "http://127.0.0.1:8000"
    settings_url = f"{base_url}/dashboard/user-dashboard/settings/"
    
    print(f"Testing access to: {settings_url}")
    
    try:
        # First try to access without login (should redirect)
        print("\n1. Testing without login...")
        response = requests.get(settings_url, timeout=5)
        print(f"   Status Code: {response.status_code}")
        print(f"   Redirect Location: {response.headers.get('Location', 'None')}")
        
        # Try to access with login (need to get login page first)
        print("\n2. Testing with login...")
        
        # Get login page
        login_url = f"{base_url}/login/"
        login_response = requests.get(login_url, timeout=5)
        print(f"   Login page status: {login_response.status_code}")
        
        # Extract CSRF token
        csrf_token = None
        if 'csrftoken' in login_response.cookies:
            csrf_token = login_response.cookies['csrftoken']
            print(f"   CSRF Token: {csrf_token}")
        
        if csrf_token:
            # Login with test credentials
            login_data = {
                'username': 'admin',  # Try with admin first
                'password': 'admin123',
                'csrfmiddlewaretoken': csrf_token
            }
            
            session = requests.Session()
            session.cookies.set('csrftoken', csrf_token)
            
            login_post = session.post(login_url, data=login_data, timeout=5)
            print(f"   Login POST status: {login_post.status_code}")
            
            # Now try settings page
            settings_response = session.get(settings_url, timeout=5)
            print(f"   Settings page status: {settings_response.status_code}")
            
            if settings_response.status_code == 200:
                print("   ✅ SUCCESS: Settings page loaded!")
                print(f"   Content length: {len(settings_response.text)}")
                
                # Check for key elements
                if 'Settings' in settings_response.text:
                    print("   ✅ Settings title found")
                if 'settings-form' in settings_response.text:
                    print("   ✅ Settings form found")
                if 'theme' in settings_response.text:
                    print("   ✅ Theme controls found")
            else:
                print(f"   ❌ FAILED: Status {settings_response.status_code}")
                print(f"   Response: {settings_response.text[:200]}...")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Server not running")
    except requests.exceptions.Timeout:
        print("❌ Timeout Error: Request timed out")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    test_settings_page()
