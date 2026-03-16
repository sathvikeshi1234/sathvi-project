import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from apps.tickets.models import Ticket
from apps.users.models import User

print("=== Checking Tickets and User Data ===")

# Check all tickets
tickets = Ticket.objects.all()
print(f"Total tickets: {tickets.count()}")

for ticket in tickets[:5]:  # Show first 5 tickets
    print(f"Ticket ID: {ticket.ticket_id}, DB ID: {ticket.id}")
    print(f"  Created by: {ticket.created_by.username if ticket.created_by else 'None'} (ID: {ticket.created_by.id if ticket.created_by else 'None'})")
    print(f"  Assigned to: {ticket.assigned_to.get_full_name() if ticket.assigned_to else 'None'} (ID: {ticket.assigned_to.id if ticket.assigned_to else 'None'})")
    print(f"  Title: {ticket.title}")
    print()

print("=== Checking Users ===")
users = User.objects.all()
print(f"Total users: {users.count()}")

for user in users[:5]:  # Show first 5 users
    print(f"User: {user.username} (ID: {user.id})")
    print(f"  Email: {user.email}")
    print(f"  Is staff: {user.is_staff}")
    print()

print("=== Checking API Data Structure ===")
# Simulate what the API would return
from django.core import serializers
from django.http import JsonResponse
import json

# Create a list like the API would
tickets_data = []
for ticket in tickets:
    tickets_data.append({
        'id': ticket.id,
        'ticket_id': ticket.ticket_id,
        'title': ticket.title,
        'status': ticket.status,
        'priority': ticket.priority,
        'created_at': ticket.created_at.isoformat(),
        'created_by_id': ticket.created_by.id if ticket.created_by else None,
        'created_by_username': ticket.created_by.username if ticket.created_by else None,
        'assigned_to_id': ticket.assigned_to.id if ticket.assigned_to else None,
        'assigned_to_username': ticket.assigned_to.get_full_name() if ticket.assigned_to else None,
        'assigned_to_full_name': ticket.assigned_to.get_full_name() if ticket.assigned_to else None,
    })

print("Sample API data structure:")
if tickets_data:
    print(json.dumps(tickets_data[0], indent=2))
else:
    print("No tickets found")
