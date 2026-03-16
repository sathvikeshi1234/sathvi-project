import os
import sys
import django

sys.path.append('c:/Users/arikatla/Documents/temp/sathvi project/ticket-management-')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from tickets.models import ChatMessage

print("=== Testing Emoji in Database ===")

# Get some recent messages
messages = ChatMessage.objects.all().order_by('-created_at')[:5]

for msg in messages:
    print(f"\nMessage ID: {msg.id}")
    print(f"Text: '{msg.text}'")
    print(f"Text repr: {repr(msg.text)}")
    print(f"Text length: {len(msg.text)}")
    print(f"Sender: {msg.sender.username if msg.sender else 'Unknown'}")
    print(f"Created: {msg.created_at}")
    
    # Check if text contains emoji-like characters
    for i, char in enumerate(msg.text):
        if ord(char) > 127:  # Non-ASCII character (likely emoji)
            print(f"  Unicode char at position {i}: '{char}' (U+{ord(char):04X})")
