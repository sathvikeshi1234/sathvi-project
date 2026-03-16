import os
import sys
import django

sys.path.append('c:/Users/arikatla/Documents/temp/sathvi project/ticket-management-')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from tickets.models import ChatMessage

print("=== Testing Emoji Insert ===")

# Get admin and user
admin = User.objects.filter(is_staff=True).first()
user = User.objects.filter(is_staff=False).first()

if admin and user:
    print(f"Admin: {admin.username} (ID: {admin.id})")
    print(f"User: {user.username} (ID: {user.id})")
    
    # Create a test message with emoji
    test_text = "Hello 😀 😊 🎉"
    print(f"Creating message with text: '{test_text}'")
    
    message = ChatMessage.objects.create(
        sender=admin,
        recipient=user,
        ticket_id="TEST001",
        text=test_text,
        is_read=False
    )
    
    print(f"Message created with ID: {message.id}")
    print(f"Stored text: '{message.text}'")
    print(f"Stored text repr: {repr(message.text)}")
    print(f"Text contains emoji: {'😀' in message.text}")
    
    # Test JSON serialization
    import json
    message_data = {
        'id': message.id,
        'text': message.text,
        'direction': 'sent',
        'sender_id': message.sender_id,
        'is_read': message.is_read,
        'time': message.created_at.astimezone().strftime('%I:%M %p'),
        'created_at': message.created_at.isoformat(),
        'ticket_id': message.ticket_id,
    }
    
    json_str = json.dumps(message_data, ensure_ascii=False)
    print(f"JSON serialized: {json_str}")
    
    # Test deserialization
    parsed = json.loads(json_str)
    print(f"Parsed text: '{parsed['text']}'")
    print(f"Emoji preserved in JSON: {'😀' in parsed['text']}")
    
else:
    print("Could not find admin and user for testing")
