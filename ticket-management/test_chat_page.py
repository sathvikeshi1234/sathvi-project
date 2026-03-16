#!/usr/bin/env python
"""
Test script to verify the chat page loads correctly
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
from tickets.models import Ticket

User = get_user_model()

def test_chat_page():
    print("Testing User Chat Page...")
    
    # Create test users
    admin_role, _ = Role.objects.get_or_create(name='Admin')
    user_role, _ = Role.objects.get_or_create(name='User')
    
    # Create admin user
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
    
    # Create customer user
    customer_user, created = User.objects.get_or_create(
        username='customer',
        defaults={
            'email': 'customer@test.com',
            'first_name': 'Customer',
            'last_name': 'User',
        }
    )
    if created:
        customer_user.set_password('customer123')
        customer_user.save()
        UserProfile.objects.get_or_create(user=customer_user, defaults={'role': user_role})
    
    # Create a test ticket
    ticket, created = Ticket.objects.get_or_create(
        ticket_id='TEST-001',
        defaults={
            'title': 'Test Ticket for Chat',
            'description': 'This is a test ticket',
            'created_by': customer_user,
            'status': 'Open',
        }
    )
    
    # Test the chat page as customer
    client = Client()
    client.force_login(customer_user)
    
    response = client.get('/dashboard/user-dashboard/chat/')
    print(f"Chat Page Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("[SUCCESS] Chat page loads successfully!")
        
        # Check for key content
        content = response.content.decode()
        if 'fileUpload' in content:
            print("[OK] File upload input found")
        if 'attachFileBtn' in content:
            print("[OK] Attach file button found")
        if 'file-previews' in content:
            print("[OK] File preview area found")
        if 'chat.js' in content:
            print("[OK] Chat JavaScript included")
        if 'chat.css' in content:
            print("[OK] Chat CSS included")
            
        print(f"Page content length: {len(content)} characters")
        
    else:
        print(f"[ERROR] Page failed to load: {response.status_code}")
        try:
            print(f"Response: {response.content.decode()[:500]}...")
        except:
            print(f"Response: {response.content[:500]}...")

if __name__ == '__main__':
    test_chat_page()
