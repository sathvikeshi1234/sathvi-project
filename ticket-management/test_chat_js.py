#!/usr/bin/env python
"""
Test to verify chat JavaScript elements are properly loaded
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

def test_chat_javascript():
    print("Testing Chat JavaScript Integration...")
    
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
        content = response.content.decode()
        
        # Check for critical JavaScript elements
        checks = [
            ('USER_CHAT_CONTACT_ID', 'Contact ID variable'),
            ('setupFileUploadHandlers', 'File upload handler function'),
            ('attachFileBtn', 'Attach file button'),
            ('fileUpload', 'File input element'),
            ('filePreviews', 'File preview area'),
            ('handleFileSelect', 'File selection handler'),
            ('FormData', 'FormData for file uploads'),
            ('files', 'Files parameter in API call'),
        ]
        
        print("\nJavaScript Elements Check:")
        all_found = True
        for element, description in checks:
            if element in content:
                print(f"[OK] {description}: Found")
            else:
                print(f"[MISSING] {description}: Not found")
                all_found = False
        
        # Check for proper file upload flow
        upload_flow_checks = [
            ('attachFileBtn.addEventListener', 'Attach button event listener'),
            ('fileUpload.click()', 'File input click trigger'),
            ('fileUpload.addEventListener', 'File input change listener'),
            ('handleFileSelect', 'File selection handler'),
            ('filePreviews.style.display', 'File preview visibility'),
            ('formData.append(\'files\')', 'Files added to FormData'),
            ('clearFilePreviews()', 'File preview cleanup'),
        ]
        
        print("\nFile Upload Flow Check:")
        for element, description in upload_flow_checks:
            if element in content:
                print(f"[OK] {description}: Found")
            else:
                print(f"[MISSING] {description}: Not found")
                all_found = False
        
        # Check for demo vs real API section
        if 'if (contactId)' in content:
            print("[OK] Real API section detected")
        else:
            print("[MISSING] Real API section not found")
            all_found = False
        
        if 'setupFileUploadHandlers()' in content:
            print("[OK] File upload handlers being called")
        else:
            print("[MISSING] File upload handlers not being called")
            all_found = False
        
        if all_found:
            print("\n[SUCCESS] All JavaScript elements are properly integrated!")
        else:
            print("\n[WARNING] Some JavaScript elements may be missing")
            
    else:
        print(f"[ERROR] Chat page failed to load: {response.status_code}")

if __name__ == '__main__':
    test_chat_javascript()
