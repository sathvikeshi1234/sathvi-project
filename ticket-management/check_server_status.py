#!/usr/bin/env python
"""
Check server status and run a simple test server
"""
import os
import sys
import subprocess
import time
import requests

def check_server_running():
    """Check if Django server is running"""
    try:
        response = requests.get('http://127.0.0.1:8000/', timeout=5)
        print(f"Server is running - Status: {response.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print("Server is not running on http://127.0.0.1:8000")
        return False
    except Exception as e:
        print(f"Error checking server: {e}")
        return False

def test_urls_with_server():
    """Test URLs with actual server"""
    base_url = "http://127.0.0.1:8000"
    
    test_urls = [
        ('/', 'Home page'),
        ('/login/', 'User login'),
        ('/admin-login/', 'Admin login'),
        ('/user-login/', 'User login separate'),
        ('/agent-login/', 'Agent login'),
        ('/superadmin/login/', 'Superadmin login'),
        ('/admin/', 'Django admin'),
    ]
    
    print("\n=== TESTING URLS WITH LIVE SERVER ===")
    
    for url_path, description in test_urls:
        full_url = base_url + url_path
        try:
            response = requests.get(full_url, timeout=10, allow_redirects=False)
            print(f"{description:20} {url_path:25} -> Status: {response.status_code}")
            if response.status_code in [301, 302]:
                location = response.headers.get('Location', 'Unknown')
                print(f"{'':20} {'':25} -> Redirects to: {location}")
        except Exception as e:
            print(f"{description:20} {url_path:25} -> ERROR: {e}")

def main():
    print("DJANGO SERVER URL CHECK")
    print("=" * 50)
    
    # Check if server is running
    if not check_server_running():
        print("\nServer is not running. Please start the Django server:")
        print("  cd \"c:/Users/arikatla/Documents/temp/sathvi project/ticket-management-\"")
        print("  python manage.py runserver")
        print("\nThen run this script again to test URLs.")
        return
    
    # Test URLs with live server
    test_urls_with_server()
    
    print("\n=== TROUBLESHOOTING TIPS ===")
    print("If URLs are not working:")
    print("1. Make sure Django server is running: python manage.py runserver")
    print("2. Check for syntax errors in URL files")
    print("3. Verify view functions exist and work properly")
    print("4. Check for middleware issues")
    print("5. Clear browser cache and try again")
    print("6. Try accessing URLs directly in browser")

if __name__ == "__main__":
    main()
