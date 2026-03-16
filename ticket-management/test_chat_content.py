#!/usr/bin/env python
"""
Test to verify the actual content being served to the browser
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

def test_chat_content():
    print("Testing Actual Chat Content...")
    
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
        
        # Check for the critical bootstrap data
        if 'USER_CHAT_CONTACT_ID' in content:
            print("[OK] USER_CHAT_CONTACT_ID found")
            
            # Extract the contact ID value
            import re
            contact_id_match = re.search(r'USER_CHAT_CONTACT_ID\s*=\s*parseInt\(el\.getAttribute\([\'"]data-contact-id[\'"]\)\s*\|\s*[\'"]\s*,\s*10\)', content)
            if contact_id_match:
                print("[OK] Contact ID assignment found")
            else:
                print("[MISSING] Contact ID assignment")
        else:
            print("[MISSING] USER_CHAT_CONTACT_ID not found")
        
        # Check for setupFileUploadHandlers function
        if 'function setupFileUploadHandlers()' in content:
            print("[OK] setupFileUploadHandlers function found")
        else:
            print("[MISSING] setupFileUploadHandlers function not found")
        
        # Check if the function is being called
        if 'setupFileUploadHandlers();' in content:
            print("[OK] setupFileUploadHandlers being called")
        else:
            print("[MISSING] setupFileUploadHandlers not being called")
        
        # Check for the real API section
        if 'if (contactId)' in content:
            print("[OK] Real API section found")
            
            # Check for FormData usage
            if 'new FormData()' in content:
                print("[OK] FormData usage found")
            else:
                print("[MISSING] FormData usage not found")
            
            # Check for files parameter
            if 'formData.append(\'files\'' in content:
                print("[OK] Files parameter found")
            else:
                print("[MISSING] Files parameter not found")
        else:
            print("[MISSING] Real API section not found")
        
        # Check for file upload elements
        file_elements = [
            'attachFileBtn.addEventListener',
            'fileUpload.click()',
            'fileUpload.addEventListener',
            'handleFileSelect'
        ]
        
        print("\nFile Upload Elements:")
        for element in file_elements:
            if element in content:
                print(f"[OK] {element}: Found")
            else:
                print(f"[MISSING] {element}: Not found")
        
        # Check for the demo section (should not be used when contactId exists)
        if 'Sample data for demonstration' in content:
            print("[WARNING] Demo section found (should not be used)")
        else:
            print("[OK] No demo section found")
            
    else:
        print(f"[ERROR] Chat page failed to load: {response.status_code}")

if __name__ == '__main__':
    test_chat_content()
