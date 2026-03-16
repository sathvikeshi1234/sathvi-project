#!/usr/bin/env python

import os
import sys
import django

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from tickets.models import ChatMessage

def test_chat_api_response():
    """Test what the chat API returns for messages"""
    
    print("=== Testing Chat API Response ===")
    
    # Get a sample user
    try:
        user = User.objects.first()
        if not user:
            print("No users found in database")
            return
            
        print(f"Current user: {user.username} (ID: {user.id})")
        
        # Get some chat messages
        messages = ChatMessage.objects.all()[:5]
        
        print(f"\nFound {messages.count()} chat messages:")
        
        for msg in messages:
            print(f"  - ID: {msg.id}")
            print(f"    Sender: {msg.sender.username if msg.sender else 'Unknown'} (ID: {msg.sender_id})")
            print(f"    Recipient: {msg.recipient.username if msg.recipient else 'Unknown'} (ID: {msg.recipient_id})")
            print(f"    Text: {msg.text[:50]}...")
            print(f"    Is Read: {msg.is_read}")
            print(f"    Direction: {'sent' if msg.sender_id == user.id else 'received'}")
            print(f"    Created: {msg.created_at}")
            print()
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_chat_api_response()
