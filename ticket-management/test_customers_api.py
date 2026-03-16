#!/usr/bin/env python
"""
Test script to verify the customers API endpoint is working
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

def test_customers_api():
    print("Testing Customers API...")
    
    # Create test data if needed
    admin_role, _ = Role.objects.get_or_create(name='Admin')
    user_role, _ = Role.objects.get_or_create(name='User')
    
    # Create admin user if not exists
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
    
    # Create test customers if not exist
    for i in range(3):
        customer, created = User.objects.get_or_create(
            username=f'customer{i+1}',
            defaults={
                'email': f'customer{i+1}@test.com',
                'first_name': f'Customer',
                'last_name': f'{i+1}',
            }
        )
        if created:
            customer.set_password('customer123')
            customer.save()
            UserProfile.objects.get_or_create(user=customer, defaults={'role': user_role})
    
    # Test the API
    client = Client()
    
    # Login as admin
    client.force_login(admin_user)
    
    # Test customers API
    response = client.get('/api/customers/')
    print(f"Status Code: {response.status_code}")
    
    data = None
    if response.status_code == 200:
        data = response.json()
        print(f"Total customers: {data.get('total', 0)}")
        print(f"Results: {len(data.get('results', []))}")
        
        if data.get('results'):
            print("\nFirst customer:")
            customer = data['results'][0]
            print(f"  ID: {customer.get('id')}")
            print(f"  Name: {customer.get('name')}")
            print(f"  Email: {customer.get('email')}")
            print(f"  Tickets: {customer.get('tickets_count', 0)}")
        
        print(f"\n[SUCCESS] Customers API is working!")
    else:
        print(f"[ERROR] Status: {response.status_code}")
        if response.status_code == 302:
            print("Redirect detected - user may not be logged in properly")
            # Try to follow redirect
            if response.has_header('location'):
                redirect_url = response['location']
                print(f"Redirecting to: {redirect_url}")
                response = client.get(redirect_url)
                print(f"After redirect - Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
        else:
            try:
                print(f"Response: {response.content.decode()}")
            except:
                print(f"Response: {response.content}")
    
    # Test user detail API
    if data.get('results'):
        customer_id = data['results'][0]['id']
        response = client.get(f'/api/users/{customer_id}/')
        print(f"\nUser Detail API Status: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"[SUCCESS] User Detail API working for {user_data.get('name')}")
        else:
            print(f"[ERROR] User Detail API Status: {response.status_code}")
            try:
                print(f"Response: {response.content.decode()}")
            except:
                print(f"Response: {response.content}")

if __name__ == '__main__':
    test_customers_api()
