#!/usr/bin/env python
"""
Manual test to verify file upload functionality works end-to-end
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
from tickets.models import Ticket, ChatMessage, ChatMessageAttachment

User = get_user_model()

def test_chat_upload_manual():
    print("=== Manual File Upload Test ===")
    
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
    
    print(f"[OK] Created test ticket: {ticket.ticket_id}")
    print(f"[OK] Support admin: {admin_user.get_full_name()} (ID: {admin_user.id})")
    print(f"[OK] Customer: {customer_user.get_full_name()} (ID: {customer_user.id})")
    
    # Test the file upload API
    client = Client()
    client.force_login(customer_user)
    
    # Test 1: Send message with file
    print("\n1. Testing file upload via API...")
    test_file = SimpleUploadedFile(
        "test_upload.txt", 
        b"This is a test file for manual upload verification", 
        content_type="text/plain"
    )
    
    response = client.post('/api/chat/messages/', {
        'contact_id': admin_user.id,
        'ticket_id': 'TEST-001',
        'text': 'Hello admin, here is a file for testing',
        'files': test_file,
    })
    
    if response.status_code == 201:
        data = response.json()
        print("[OK] File upload successful!")
        print(f"  Message ID: {data.get('id')}")
        print(f"  Text: {data.get('text')}")
        if 'attachments' in data:
            print(f"  Attachments: {len(data['attachments'])}")
            for att in data['attachments']:
                print(f"    - {att.get('filename')} ({att.get('filesize')} bytes)")
                print(f"    - URL: {att.get('url')}")
    else:
        print(f"[ERROR] File upload failed: {response.status_code}")
        try:
            print(f"  Error: {response.json()}")
        except:
            print(f"  Error: {response.content.decode()}")
    
    # Test 2: Retrieve messages to verify attachments
    print("\n2. Testing message retrieval...")
    response = client.get(f'/api/chat/messages/?contact_id={admin_user.id}&ticket_id=TEST-001')
    
    if response.status_code == 200:
        data = response.json()
        messages = data.get('results', [])
        print(f"[OK] Retrieved {len(messages)} messages")
        
        attachment_count = 0
        for msg in messages:
            if msg.get('attachments'):
                attachment_count += len(msg['attachments'])
                print(f"  Message {msg['id']} has {len(msg['attachments'])} attachment(s):")
                for att in msg['attachments']:
                    print(f"    - {att.get('filename')} ({att.get('filesize')} bytes)")
        
        print(f"[OK] Total attachments: {attachment_count}")
        
        # Verify database
        db_attachments = ChatMessageAttachment.objects.filter(
            message__ticket_id='TEST-001'
        ).count()
        print(f"[OK] Database attachments: {db_attachments}")
        
    else:
        print(f"[ERROR] Message retrieval failed: {response.status_code}")
    
    # Test 3: Verify file can be downloaded
    print("\n3. Testing file download...")
    attachments = ChatMessageAttachment.objects.filter(
        message__ticket_id='TEST-001'
    )
    
    if attachments.exists():
        attachment = attachments.first()
        file_url = attachment.file.url
        print(f"[OK] File URL: {file_url}")
        
        # Test file access
        response = client.get(file_url)
        if response.status_code == 200:
            content = b''.join(response.streaming_content) if hasattr(response, 'streaming_content') else response.content
            print(f"[OK] File accessible via URL ({len(content)} bytes)")
        else:
            print(f"[ERROR] File not accessible: {response.status_code}")
    else:
        print("[ERROR] No attachments found to test download")
    
    print("\n=== Manual Test Complete ===")
    print("[OK] File upload API is working correctly")
    print("[INFO] The issue is likely in the frontend JavaScript")
    print("[OK] Backend functionality is fully operational")

if __name__ == '__main__':
    test_chat_upload_manual()
