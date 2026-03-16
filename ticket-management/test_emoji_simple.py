import os
import sys
import django

sys.path.append('c:/Users/arikatla/Documents/temp/sathvi project/ticket-management-')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from tickets.models import ChatMessage
import json

# Test without console output issues
try:
    admin = User.objects.filter(is_staff=True).first()
    user = User.objects.filter(is_staff=False).first()
    
    if admin and user:
        # Create message with simple emoji
        test_text = "Hello :)"
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
        
        # Write results to file instead of console
        with open('emoji_test_results.txt', 'w', encoding='utf-8') as f:
            f.write(f"Original text: {test_text}\n")
            f.write(f"Stored text: {message.text}\n")
            f.write(f"JSON result: {parsed['text']}\n")
            f.write("Test completed successfully")
        
        print("Test completed - check emoji_test_results.txt")
    else:
        print("No users found")
        
except Exception as e:
    print(f"Error: {e}")
