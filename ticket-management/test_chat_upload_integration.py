#!/usr/bin/env python
"""
Integration test for chat file upload functionality
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

def test_chat_upload_integration():
    print("Testing Chat Upload Integration...")
    
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
    
    # Test as customer user
    client = Client()
    client.force_login(customer_user)
    
    # Test 1: Send message with text only
    print("\n1. Testing text-only message...")
    response = client.post('/api/chat/messages/', {
        'contact_id': admin_user.id,
        'ticket_id': 'TEST-001',
        'text': 'Hello admin, this is a text-only message',
    })
    
    if response.status_code == 201:
        print("[OK] Text message sent successfully")
    else:
        print(f"[ERROR] Text message failed: {response.status_code}")
    
    # Test 2: Send message with file only
    print("\n2. Testing file-only message...")
    test_file = SimpleUploadedFile(
        "test_upload.txt", 
        b"This is a test file for upload", 
        content_type="text/plain"
    )
    
    response = client.post('/api/chat/messages/', {
        'contact_id': admin_user.id,
        'ticket_id': 'TEST-001',
        'files': test_file,
    })
    
    if response.status_code == 201:
        data = response.json()
        print("[OK] File-only message sent successfully")
        print(f"  Message ID: {data.get('id')}")
        if 'attachments' in data:
            print(f"  Attachments: {len(data['attachments'])}")
            for att in data['attachments']:
                print(f"    - {att.get('filename')} ({att.get('filesize')} bytes)")
    else:
        print(f"[ERROR] File-only message failed: {response.status_code}")
    
    # Test 3: Send message with both text and file
    print("\n3. Testing message with text + file...")
    test_file2 = SimpleUploadedFile(
        "document.pdf", 
        b"%PDF-1.4 test content", 
        content_type="application/pdf"
    )
    
    response = client.post('/api/chat/messages/', {
        'contact_id': admin_user.id,
        'ticket_id': 'TEST-001',
        'text': 'Here is a document for you',
        'files': test_file2,
    })
    
    if response.status_code == 201:
        data = response.json()
        print("[OK] Text + file message sent successfully")
        print(f"  Message ID: {data.get('id')}")
        print(f"  Text: {data.get('text')}")
        if 'attachments' in data:
            print(f"  Attachments: {len(data['attachments'])}")
            for att in data['attachments']:
                print(f"    - {att.get('filename')} ({att.get('filesize')} bytes)")
    else:
        print(f"[ERROR] Text + file message failed: {response.status_code}")
    
    # Test 4: Retrieve all messages and verify attachments
    print("\n4. Testing message retrieval...")
    response = client.get(f'/api/chat/messages/?contact_id={admin_user.id}&ticket_id=TEST-001')
    
    if response.status_code == 200:
        data = response.json()
        messages = data.get('results', [])
        print(f"[OK] Retrieved {len(messages)} messages")
        
        attachment_count = 0
        for msg in messages:
            if msg.get('attachments'):
                attachment_count += len(msg['attachments'])
                print(f"  Message {msg['id']}: {len(msg['attachments'])} attachments")
                for att in msg['attachments']:
                    print(f"    - {att.get('filename')} (URL: {att.get('url')})")
        
        print(f"[OK] Total attachments: {attachment_count}")
        
        # Verify database
        db_attachments = ChatMessageAttachment.objects.filter(
            message__ticket_id='TEST-001'
        ).count()
        print(f"[OK] Database attachments: {db_attachments}")
        
    else:
        print(f"[ERROR] Message retrieval failed: {response.status_code}")
    
    # Test 5: Test file size validation
    print("\n5. Testing file size validation...")
    large_file = SimpleUploadedFile(
        "large_file.txt", 
        b"x" * (11 * 1024 * 1024),  # 11MB file
        content_type="text/plain"
    )
    
    response = client.post('/api/chat/messages/', {
        'contact_id': admin_user.id,
        'ticket_id': 'TEST-001',
        'text': 'This should fail due to large file',
        'files': large_file,
    })
    
    if response.status_code == 201:
        # Large file should be skipped but message still created
        data = response.json()
        attachments = data.get('attachments', [])
        if len(attachments) == 0:
            print("[OK] Large file correctly rejected")
        else:
            print("[ERROR] Large file was accepted (should be rejected)")
    else:
        print(f"[ERROR] Large file test failed: {response.status_code}")
    
    print("\n=== Integration Test Complete ===")

if __name__ == '__main__':
    test_chat_upload_integration()
