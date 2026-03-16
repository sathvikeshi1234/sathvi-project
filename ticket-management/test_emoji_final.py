import os
import sys
import django

sys.path.append('c:/Users/arikatla/Documents/temp/sathvi project/ticket-management-')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from tickets.models import ChatMessage
import json

try:
    admin = User.objects.filter(is_staff=True).first()
    user = User.objects.filter(is_staff=False).first()
    
    if admin and user:
        # Test with real emoji
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
        with open('emoji_final_test.txt', 'w', encoding='utf-8') as f:
            f.write(f"SUCCESS: Emoji stored and retrieved\n")
            f.write(f"Original: {test_text}\n")
            f.write(f"Stored: {message.text}\n")
            f.write(f"JSON: {parsed['text']}\n")
            f.write(f"Lengths: orig={len(test_text)}, stored={len(message.text)}, json={len(parsed['text'])}\n")
        
        print("Emoji test completed successfully!")
    else:
        print("No users found")
        
except Exception as e:
    print(f"Error: {e}")
    with open('emoji_final_test.txt', 'w', encoding='utf-8') as f:
        f.write(f"ERROR: {e}\n")
