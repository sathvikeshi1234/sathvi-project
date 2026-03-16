#!/usr/bin/env python
"""
Debug URL issues
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
from django.conf import settings

def debug_url_patterns():
    """Debug all URL patterns"""
    print("=== DEBUGGING URL PATTERNS ===\n")
    
    resolver = get_resolver()
    
    def print_patterns(patterns, prefix="", level=0):
        """Recursively print URL patterns"""
        for pattern in patterns:
            indent = "  " * level
            if hasattr(pattern, 'url_patterns'):
                # This is an include()
                print(f"{indent}{prefix}{pattern.pattern} -> include({pattern.app_name or pattern.namespace})")
                if pattern.url_patterns:
                    print_patterns(pattern.url_patterns, prefix, level + 1)
            else:
                # This is a regular path
                view_name = getattr(pattern.callback, '__name__', str(pattern.callback))
                print(f"{indent}{prefix}{pattern.pattern} -> {view_name}")
    
    print("All URL Patterns:")
    print_patterns(resolver.url_patterns)

def test_specific_urls():
    """Test specific URLs that should work"""
    print("\n=== TESTING SPECIFIC URLS ===\n")
    
    client = Client()
    
    # Test URLs that should definitely work
    test_urls = [
        ('/', 'Home page'),
        ('/login/', 'User login'),
        ('/admin-login/', 'Admin login'),
        ('/user-login/', 'User login separate'),
        ('/agent-login/', 'Agent login'),
        ('/superadmin/login/', 'Superadmin login'),
        ('/admin/', 'Django admin'),
    ]
    
    for url, description in test_urls:
        try:
            response = client.get(url)
            print(f"{description:20} {url:25} -> Status: {response.status_code}")
            if response.status_code == 302:
                print(f"{'':20} {'':25} -> Redirects to: {response.get('Location', 'Unknown')}")
            elif response.status_code == 404:
                print(f"{'':20} {'':25} -> NOT FOUND")
        except Exception as e:
            print(f"{description:20} {url:25} -> ERROR: {e}")

def check_url_reverse():
    """Check URL reverse lookups"""
    print("\n=== URL REVERSE LOOKUPS ===\n")
    
    try:
        print("Users namespace:")
        print(f"  login: {reverse('users:login')}")
        print(f"  admin_login: {reverse('users:admin_login')}")
        print(f"  user_login: {reverse('users:user_login')}")
        print(f"  agent_login: {reverse('users:agent_login')}")
        
        print("\nSuperadmin namespace:")
        print(f"  superadmin_login: {reverse('superadmin:superadmin_login')}")
        print(f"  superadmin_dashboard: {reverse('superadmin:superadmin_dashboard')}")
        
    except Exception as e:
        print(f"Reverse lookup error: {e}")

def check_app_configs():
    """Check app configurations"""
    print("\n=== APP CONFIGURATIONS ===\n")
    
    from django.apps import apps
    
    for app_config in apps.get_app_configs():
        if app_config.name in ['users', 'superadmin', 'dashboards']:
            print(f"App: {app_config.name}")
            print(f"  Module: {app_config.module}")
            print(f"  Path: {app_config.path}")
            print()

if __name__ == "__main__":
    debug_url_patterns()
    test_specific_urls()
    check_url_reverse()
    check_app_configs()
