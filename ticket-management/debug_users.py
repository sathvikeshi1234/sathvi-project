import os
import sys
import django

sys.path.append('c:/Users/arikatla/Documents/temp/sathvi project/ticket-management-')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from tickets.models import ChatMessage

print('=== All Users ===')
for user in User.objects.all():
    print(f'User: {user.username} (ID: {user.id}) - Staff: {user.is_staff}, Super: {user.is_superuser}')

print('\n=== Admin Users ===')
admins = User.objects.filter(is_staff=True) | User.objects.filter(is_superuser=True)
for admin in admins:
    print(f'Admin: {admin.username} (ID: {admin.id}) - Staff: {admin.is_staff}, Super: {admin.is_superuser}')

print('\n=== Chat Messages for Admin (ID: 8) ===')
admin_messages = ChatMessage.objects.filter(sender_id=8)[:3]
for msg in admin_messages:
    recipient_name = msg.recipient.username if msg.recipient else "Unknown"
    print(f'From Admin to {recipient_name}: {msg.text[:30]}...')
