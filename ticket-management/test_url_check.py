#!/usr/bin/env python
"""
Test script to check admin, user, and superadmin URLs
"""
import os
import sys
import django
from django.test import Client
from django.urls import reverse
from django.conf import settings

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def check_urls():
    """Check if URLs are accessible and working correctly"""
    client = Client()
    
    print("=== URL Configuration Check ===\n")
    
    # Test Admin URLs
    print("1. ADMIN URLS:")
    print(f"   - Admin panel: /admin/")
    try:
        response = client.get('/admin/')
        print(f"   Status: {response.status_code}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test User URLs
    print("\n2. USER URLS:")
    user_urls = [
        ('login', '/login/'),
        ('signup', '/signup/'),
        ('admin-login', '/admin-login/'),
        ('user-login', '/user-login/'),
        ('agent-login', '/agent-login/'),
    ]
    
    for name, url in user_urls:
        print(f"   - {name}: {url}")
        try:
            response = client.get(url)
            print(f"     Status: {response.status_code}")
        except Exception as e:
            print(f"     Error: {e}")
    
    # Test Superadmin URLs
    print("\n3. SUPERADMIN URLS:")
    superadmin_urls = [
        ('login', '/superadmin/login/'),
        ('signup', '/superadmin/signup/'),
        ('dashboard', '/superadmin/dashboard/'),
    ]
    
    for name, url in superadmin_urls:
        print(f"   - {name}: {url}")
        try:
            response = client.get(url)
            print(f"     Status: {response.status_code}")
        except Exception as e:
            print(f"     Error: {e}")
    
    print("\n=== URL Reverse Check ===")
    
    # Test reverse URL resolution
    try:
        print(f"Users namespace - login: {reverse('users:login')}")
        print(f"Users namespace - admin_login: {reverse('users:admin_login')}")
        print(f"Users namespace - user_login: {reverse('users:user_login')}")
        print(f"Superadmin namespace - login: {reverse('superadmin:superadmin_login')}")
        print(f"Superadmin namespace - dashboard: {reverse('superadmin:superadmin_dashboard')}")
    except Exception as e:
        print(f"Reverse URL error: {e}")

if __name__ == "__main__":
    check_urls()
