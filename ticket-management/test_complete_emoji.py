import os
import sys
import django

sys.path.append('c:/Users/arikatla/Documents/temp/sathvi project/ticket-management-')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from tickets.models import ChatMessage

try:
    admin = User.objects.filter(is_staff=True).first()
    user = User.objects.filter(is_staff=False).first()
    
    if admin and user:
        # Create several test messages with different emojis
        test_messages = [
            "Hello 😀",
            "How are you 😊?",
            "Great! 🎉",
            "Thanks 🙏",
            "Bye 👋"
        ]
        
        for i, text in enumerate(test_messages):
            message = ChatMessage.objects.create(
                sender=admin,
                recipient=user,
                ticket_id=f"TEST{i+1:03d}",
                text=text,
                is_read=False
            )
            print(f"Created message {i+1}: ID {message.id}")
        
        print("All emoji test messages created successfully!")
        print("Check the admin chat page to see if emojis display correctly")
        
    else:
        print("No users found")
        
except Exception as e:
    print(f"Error: {e}")
