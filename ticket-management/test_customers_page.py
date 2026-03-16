#!/usr/bin/env python
"""
Test script to verify the customers page loads correctly
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from users.models import UserProfile, Role

User = get_user_model()

def test_customers_page():
    print("Testing Customers Page...")
    
    # Get or create admin user
    admin_role, _ = Role.objects.get_or_create(name='Admin')
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@test.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        UserProfile.objects.get_or_create(user=admin_user, defaults={'role': admin_role})
    
    # Test the page
    client = Client()
    client.force_login(admin_user)
    
    # Test customers page
    response = client.get('/dashboard/admin-dashboard/customers.html/')
    print(f"Page Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("[SUCCESS] Customers page loads successfully!")
        
        # Check for key content
        content = response.content.decode()
        if 'customers-table' in content:
            print("[OK] Customers table found in template")
        if 'loadCustomers()' in content:
            print("[OK] JavaScript loadCustomers function found")
        if '/api/customers/' in content:
            print("[OK] API endpoint reference found")
        if 'customer-search' in content:
            print("[OK] Search functionality found")
            
        print(f"Page content length: {len(content)} characters")
        
    else:
        print(f"[ERROR] Page failed to load: {response.status_code}")
        try:
            print(f"Response: {response.content.decode()[:500]}...")
        except:
            print(f"Response: {response.content[:500]}...")

if __name__ == '__main__':
    test_customers_page()
