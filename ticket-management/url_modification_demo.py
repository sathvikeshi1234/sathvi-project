#!/usr/bin/env python
"""
Demonstrate URL modification behavior
"""
import os
import sys
import django

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.urls import reverse
from django.test import Client

def show_current_urls():
    """Show current URL configuration"""
    print("=== CURRENT URLS ===")
    try:
        print(f"users:login -> {reverse('users:login')}")
        print(f"users:admin_login -> {reverse('users:admin_login')}")
        print(f"superadmin:superadmin_login -> {reverse('superadmin:superadmin_login')}")
    except Exception as e:
        print(f"Error getting URLs: {e}")

def test_url_access():
    """Test URL accessibility"""
    client = Client()
    
    test_cases = [
        ('/login/', 'Original user login'),
        ('/admin-login/', 'Original admin login'),
        ('/superadmin/login/', 'Original superadmin login'),
        ('/login-test/', 'Modified user login'),
        ('/admin-login-test/', 'Modified admin login'),
        ('/superadmin/login-test/', 'Modified superadmin login'),
    ]
    
    print("\n=== URL ACCESSIBILITY TEST ===")
    for url, description in test_cases:
        try:
            response = client.get(url)
            status = "WORKS" if response.status_code == 200 else f"Status: {response.status_code}"
            print(f"{description:30} {url:25} -> {status}")
        except Exception as e:
            print(f"{description:30} {url:25} -> Error: {e}")

def main():
    print("URL MODIFICATION DEMONSTRATION")
    print("=" * 50)
    
    print("\n1. BEFORE MODIFICATION:")
    show_current_urls()
    test_url_access()
    
    print("\n" + "=" * 50)
    print("2. MODIFICATION EXPLANATION:")
    print("If you modify the URL patterns in the files:")
    print("  - apps/users/urls.py")
    print("  - apps/superadmin/urls.py")
    print("")
    print("The URLs WILL change. For example:")
    print("  Changing 'login/' to 'login-test/' in users/urls.py")
    print("  will make the old URL '/login/' return 404")
    print("  and the new URL '/login-test/' will work")
    
    print("\n3. CURRENT URL STRUCTURE:")
    print("Admin URLs:")
    print("  - Django Admin: /admin/")
    print("  - Admin Login: /admin-login/")
    print("")
    print("User URLs:")
    print("  - User Login: /login/")
    print("  - User Signup: /signup/")
    print("  - Agent Login: /agent-login/")
    print("")
    print("Superadmin URLs:")
    print("  - Superadmin Login: /superadmin/login/")
    print("  - Superadmin Dashboard: /superadmin/dashboard/")
    
    print("\n4. CONCLUSION:")
    print("YES - URLs DO change when you modify them in the URL files.")
    print("The URL configuration is directly read from these files:")
    print("  - config/urls.py (main URLconf)")
    print("  - apps/users/urls.py (user app URLs)")
    print("  - apps/superadmin/urls.py (superadmin app URLs)")

if __name__ == "__main__":
    main()
