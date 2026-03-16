#!/usr/bin/env python
"""
Test script to verify chat file upload functionality
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
from django.core.files.uploadedfile import SimpleUploadedFile
from users.models import UserProfile, Role
from tickets.models import ChatMessage, ChatMessageAttachment, Ticket

User = get_user_model()

def test_chat_file_upload():
    print("Testing Chat File Upload...")
    
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
    if created:
        print("Created test ticket")
    
    # Test file upload as customer
    client = Client()
    client.force_login(customer_user)
    
    # Create a test file
    test_file = SimpleUploadedFile(
        "test_document.txt", 
        b"This is a test file content for chat upload", 
        content_type="text/plain"
    )
    
    # Test sending message with file
    response = client.post('/api/chat/messages/', {
        'contact_id': admin_user.id,
        'ticket_id': 'TEST-001',
        'text': 'Hello admin, here is a file',
        'files': test_file,
    })
    
    print(f"File Upload Status Code: {response.status_code}")
    
    if response.status_code == 201:
        data = response.json()
        print("[SUCCESS] Message with file uploaded successfully!")
        print(f"Message ID: {data.get('id')}")
        print(f"Text: {data.get('text')}")
        
        if 'attachments' in data:
            print(f"Attachments: {len(data['attachments'])}")
            for att in data['attachments']:
                print(f"  - {att.get('filename')} ({att.get('filesize')} bytes)")
        
        # Verify attachment was created
        message = ChatMessage.objects.get(id=data['id'])
        attachments = ChatMessageAttachment.objects.filter(message=message)
        print(f"Database attachments count: {attachments.count()}")
        
    else:
        print(f"[ERROR] Upload failed: {response.status_code}")
        try:
            print(f"Response: {response.json()}")
        except:
            print(f"Response: {response.content.decode()}")
    
    # Test retrieving messages with attachments
    response = client.get(f'/api/chat/messages/?contact_id={admin_user.id}&ticket_id=TEST-001')
    print(f"\nMessages Retrieval Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Messages count: {len(data.get('results', []))}")
        
        for msg in data.get('results', []):
            if msg.get('attachments'):
                print(f"Message {msg['id']} has {len(msg['attachments'])} attachments")
                for att in msg['attachments']:
                    print(f"  - {att.get('filename')} (URL: {att.get('url')})")
    else:
        print(f"[ERROR] Failed to retrieve messages: {response.status_code}")

if __name__ == '__main__':
    test_chat_file_upload()
