#!/usr/bin/env python3
"""
Direct test to see what's happening with settings URL
"""

import requests
import time

def test_direct_access():
    base_url = "http://127.0.0.1:8000"
    settings_url = f"{base_url}/dashboard/user-dashboard/settings/"
    
    print(f"Testing direct access to: {settings_url}")
    print("=" * 60)
    
    try:
        # Test with a simple GET request
        print("Making direct GET request...")
        response = requests.get(settings_url, timeout=10, allow_redirects=False)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("SUCCESS: Page returned 200")
            content = response.text
            print(f"Content length: {len(content)}")
            
            # Look for key indicators
            if "Settings" in content:
                print("✓ Found 'Settings' in content")
            if "settings-form" in content:
                print("✓ Found 'settings-form' in content")
            if "DOCTYPE html" in content:
                print("✓ Found HTML DOCTYPE")
            if "TicketHub" in content:
                print("✓ Found 'TicketHub' title")
                
            # Show first 500 characters
            print(f"First 500 chars:\n{content[:500]}")
            
        elif response.status_code == 302:
            print("REDIRECT: Page is redirecting")
            print(f"Redirect location: {response.headers.get('Location', 'None')}")
        elif response.status_code == 404:
            print("NOT FOUND: Page returns 404")
        elif response.status_code == 500:
            print("SERVER ERROR: Page returns 500")
            print(f"Error content: {response.text[:500]}")
        else:
            print(f"UNEXPECTED: Status {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
    except requests.exceptions.ConnectionError:
        print("CONNECTION ERROR: Cannot connect to server")
        print("Make sure the Django server is running on port 8000")
    except requests.exceptions.Timeout:
        print("TIMEOUT ERROR: Request timed out")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_direct_access()
