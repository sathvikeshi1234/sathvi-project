#!/usr/bin/env python
"""
Test to verify the chat context variables
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

def test_chat_context():
    print("Testing Chat Context Variables...")
    
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
    
    # Check if support admin exists
    support_admin = User.objects.filter(is_staff=True, is_active=True).first()
    print(f"Support Admin Found: {support_admin is not None}")
    if support_admin:
        print(f"Support Admin ID: {support_admin.id}")
        print(f"Support Admin Name: {support_admin.get_full_name()}")
    
    # Check user tickets
    user_ticket_ids = list(
        Ticket.objects
        .filter(created_by=customer_user)
        .order_by('-created_at')
        .values_list('ticket_id', flat=True)
    )
    print(f"User Ticket IDs: {user_ticket_ids}")
    
    # Test the chat page as customer
    client = Client()
    client.force_login(customer_user)
    
    response = client.get('/dashboard/user-dashboard/chat/')
    print(f"Chat Page Status Code: {response.status_code}")
    
    if response.status_code == 200:
        content = response.content.decode()
        
        # Check if support_admin is being set
        if 'data-contact-id=' in content:
            print("[OK] Support admin data found in template")
            
            # Extract the contact ID
            import re
            contact_id_match = re.search(r'data-contact-id="(\d+)"', content)
            if contact_id_match:
                contact_id = contact_id_match.group(1)
                print(f"[OK] Contact ID in template: {contact_id}")
                
                # Check if the JavaScript variable is being set
                if f'window.USER_CHAT_CONTACT_ID = {contact_id}' in content:
                    print("[OK] JavaScript variable being set correctly")
                else:
                    print("[ERROR] JavaScript variable not being set correctly")
            else:
                print("[ERROR] Could not extract contact ID from template")
        else:
            print("[ERROR] No support admin data found in template")
        
        # Check for the else block (no support admin)
        if 'window.USER_CHAT_CONTACT_ID = null' in content:
            print("[ERROR] Using else block (no support admin)")
        else:
            print("[OK] Not using else block")
            
    else:
        print(f"[ERROR] Chat page failed to load: {response.status_code}")

if __name__ == '__main__':
    test_chat_context()
