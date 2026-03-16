#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from tickets.models import ChatMessage, Ticket

def debug_chat_system():
    print("=== CHAT SYSTEM DEBUG ===")
    
    # Check users
    print("\n1. USERS:")
    all_users = User.objects.all()
    for user in all_users:
        print(f"  - {user.username} (ID: {user.id}, Staff: {user.is_staff}, Superuser: {user.is_superuser}, Active: {user.is_active})")
    
    # Check staff users
    staff_users = User.objects.filter(is_staff=True)
    print(f"\n2. STAFF USERS: {staff_users.count()} found")
    for staff in staff_users:
        print(f"  - {staff.username} (ID: {staff.id})")
    
    # Check tickets
    tickets = Ticket.objects.all()
    print(f"\n3. TICKETS: {tickets.count()} found")
    for ticket in tickets[:5]:  # Show first 5
        print(f"  - {ticket.ticket_id} by {ticket.created_by.username} (Status: {ticket.status})")
    
    # Check chat messages
    messages = ChatMessage.objects.all()
    print(f"\n4. CHAT MESSAGES: {messages.count()} found")
    for msg in messages[:5]:  # Show first 5
        print(f"  - {msg.sender.username} -> {msg.recipient.username}: {msg.text[:30]}... (Ticket: {msg.ticket_id})")
    
    print("\n=== END DEBUG ===")

if __name__ == "__main__":
    debug_chat_system()
