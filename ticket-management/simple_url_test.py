#!/usr/bin/env python
"""
Simple test to check URL configuration
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

from django.urls import get_resolver, reverse
from django.test import Client

def check_url_config():
    """Check current URL configuration"""
    print("=== CURRENT URL CONFIGURATION ===\n")
    
    resolver = get_resolver()
    
    print("1. ADMIN URLS:")
    print("   - /admin/ - Django admin panel")
    
    print("\n2. USER URLS (from users app):")
    user_patterns = [
        'login',
        'signup', 
        'admin_login',
        'user_login',
        'agent_login'
    ]
    
    for pattern in user_patterns:
        try:
            url = reverse(f'users:{pattern}')
            print(f"   - {pattern}: {url}")
        except Exception as e:
            print(f"   - {pattern}: Error - {e}")
    
    print("\n3. SUPERADMIN URLS:")
    superadmin_patterns = [
        'superadmin_login',
        'superadmin_signup',
        'superadmin_dashboard'
    ]
    
    for pattern in superadmin_patterns:
        try:
            url = reverse(f'superadmin:{pattern}')
            print(f"   - {pattern}: {url}")
        except Exception as e:
            print(f"   - {pattern}: Error - {e}")
    
    print("\n=== TESTING URL ACCESSIBILITY ===")
    client = Client()
    
    test_urls = [
        ('/login/', 'User Login'),
        ('/admin-login/', 'Admin Login'),
        ('/user-login/', 'User Login (separate)'),
        ('/agent-login/', 'Agent Login'),
        ('/superadmin/login/', 'Superadmin Login'),
        ('/admin/', 'Django Admin')
    ]
    
    for url, description in test_urls:
        try:
            response = client.get(url)
            print(f"{description:25} {url:25} - Status: {response.status_code}")
        except Exception as e:
            print(f"{description:25} {url:25} - Error: {e}")

if __name__ == "__main__":
    check_url_config()
