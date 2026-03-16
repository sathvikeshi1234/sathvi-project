#!/usr/bin/env python
"""
Debug script to test the settings API endpoint
"""
import os
import sys
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from apps.dashboards.models import SiteSettings

def test_settings_api():
    print("=== Testing Settings API ===")
    
    # Get current settings
    settings = SiteSettings.get_solo()
    print(f"Current company_name: '{settings.company_name}'")
    print(f"Current currency: '{settings.currency}'")
    
    # Create test user if needed
    try:
        user = User.objects.get(username='admin')
    except User.DoesNotExist:
        user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print("Created admin user")
    
    # Test client
    client = Client()
    client.login(username='admin', password='admin123')
    
    # Test GET
    print("\n=== Testing GET ===")
    response = client.get('/dashboard/api/site-settings/')
    print(f"GET status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"GET company_name: '{data.get('company_name')}'")
        print(f"GET currency: '{data.get('currency')}'")
    else:
        print(f"GET error: {response.content}")
    
    # Test PATCH
    print("\n=== Testing PATCH ===")
    patch_data = {
        'company_name': 'Test Company Name',
        'currency': 'EUR - Euro (€)'
    }
    
    response = client.patch('/dashboard/api/site-settings/', 
                          data=json.dumps(patch_data),
                          content_type='application/json')
    print(f"PATCH status: {response.status_code}")
    print(f"PATCH response: {response.content}")
    
    # Check if settings were updated
    settings.refresh_from_db()
    print(f"\nAfter PATCH company_name: '{settings.company_name}'")
    print(f"After PATCH currency: '{settings.currency}'")

if __name__ == '__main__':
    test_settings_api()
