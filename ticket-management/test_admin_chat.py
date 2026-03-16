import os
import sys
import django
from django.db import models

sys.path.append('c:/Users/arikatla/Documents/temp/sathvi project/ticket-management-')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from tickets.models import ChatMessage

# Simulate what the API would return for Admin user (ID: 8)
admin_user = User.objects.get(id=8)
print(f"Simulating API response for: {admin_user.username} (ID: {admin_user.id})")

# Get messages where Admin is involved
admin_messages = ChatMessage.objects.filter(
    models.Q(sender_id=8) | models.Q(recipient_id=8)
).order_by('created_at')[:5]

print(f"\nFound {len(admin_messages)} messages for Admin:")

for msg in admin_messages:
    direction = 'sent' if msg.sender_id == admin_user.id else 'received'
    
    message_data = {
        'id': msg.id,
        'text': msg.text,
        'direction': direction,
        'sender_id': msg.sender_id,
        'is_read': msg.is_read,
        'time': msg.created_at.astimezone().strftime('%I:%M %p'),
        'created_at': msg.created_at.isoformat(),
        'ticket_id': msg.ticket_id,
    }
    
    print(f"\nMessage {message_data['id']}:")
    print(f"  Text: {message_data['text'][:30]}...")
    print(f"  Direction: {message_data['direction']}")
    print(f"  Sender ID: {message_data['sender_id']}")
    print(f"  Is Read: {message_data['is_read']}")
    print(f"  Current User ID: {admin_user.id}")
    print(f"  Should show ticks: {message_data['direction'] == 'sent'}")
