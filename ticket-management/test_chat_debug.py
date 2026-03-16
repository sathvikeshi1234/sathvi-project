#!/usr/bin/env python
"""
Debug test to see exactly what's happening in the chat page
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

def test_chat_debug():
    print("Debugging Chat Page...")
    
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
        
        # Print the relevant JavaScript section
        print("\n=== JavaScript Section ===")
        
        # Find the JavaScript section
        import re
        
        # Find the bootstrap div
        bootstrap_match = re.search(r'<div id="user-chat-bootstrap"[^>]*>(.*?)</div>', content, re.DOTALL)
        if bootstrap_match:
            print("Bootstrap div found:")
            print(bootstrap_match.group(0))
        
        # Find the JavaScript assignment
        js_match = re.search(r'<script>\s*\(function \(\) \{.*?\}\(\);', content, re.DOTALL)
        if js_match:
            print("\nJavaScript assignment found:")
            print(js_match.group(0))
        else:
            print("\nJavaScript assignment NOT found")
            
        # Look for any script tags
        script_matches = re.findall(r'<script>.*?</script>', content, re.DOTALL)
        print(f"\nFound {len(script_matches)} script tags:")
        for i, script in enumerate(script_matches):
            print(f"Script {i+1}:")
            print(script[:200] + "..." if len(script) > 200 else script)
        
        # Check for the specific elements
        print("\n=== Element Checks ===")
        if 'if (contactId)' in content:
            print("[OK] Real API section found in JavaScript")
        else:
            print("[ERROR] Real API section NOT found in JavaScript")
        
        if 'setupFileUploadHandlers()' in content:
            print("[OK] setupFileUploadHandlers call found")
        else:
            print("[ERROR] setupFileUploadHandlers call NOT found")
            
        # Check for the actual elements
        print("\n=== HTML Elements ===")
        if 'id="attachFileBtn"' in content:
            print("[OK] Attach file button found")
        else:
            print("[ERROR] Attach file button NOT found")
            
        if 'id="fileUpload"' in content:
            print("[OK] File input found")
        else:
            print("[ERROR] File input NOT found")
            
        if 'id="filePreviews"' in content:
            print("[OK] File preview area found")
        else:
            print("[ERROR] File preview area NOT found")
            
    else:
        print(f"[ERROR] Chat page failed to load: {response.status_code}")

if __name__ == '__main__':
    test_chat_debug()
