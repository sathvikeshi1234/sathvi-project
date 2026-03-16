import os
import sys
import django

sys.path.append('c:/Users/arikatla/Documents/temp/sathvi project/ticket-management-')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from tickets.models import ChatMessage
import json

# Test with real emojis
try:
    admin = User.objects.filter(is_staff=True).first()
    user = User.objects.filter(is_staff=False).first()
    
    if admin and user:
        # Create message with real emojis
        test_text = "Hello 😀"
        message = ChatMessage.objects.create(
            sender=admin,
            recipient=user,
            ticket_id="TEST001",
            text=test_text,
            is_read=False
        )
        
        # Test JSON serialization
        message_data = {
            'id': message.id,
            'text': message.text,
            'direction': 'sent'
        }
        
        json_str = json.dumps(message_data, ensure_ascii=False)
        parsed = json.loads(json_str)
        
        # Write results to file
        with open('real_emoji_test.txt', 'w', encoding='utf-8') as f:
            f.write(f"Original: {test_text}\n")
            f.write(f"Stored: {message.text}\n")
            f.write(f"JSON: {parsed['text']}\n")
            f.write(f"Has emoji: {'😀' in parsed['text']}\n")
        
        print("Real emoji test completed - check real_emoji_test.txt")
    else:
        print("No users found")
        
except Exception as e:
    print(f"Error: {e}")
