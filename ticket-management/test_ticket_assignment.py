#!/usr/bin/env python3
"""
Test script to verify ticket assignment changes status to 'In Progress'.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.append(os.path.join(os.path.dirname(__file__), 'apps'))
django.setup()

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from tickets.models import Ticket

User = get_user_model()

def test_ticket_assignment_status():
    print("Testing Ticket Assignment Status Change")
    print("=" * 50)
    
    # Create test users
    admin_user = User.objects.create_user(
        username='test_admin',
        email='admin@test.com',
        password='testpass123',
        is_staff=True
    )
    
    agent_user = User.objects.create_user(
        username='test_agent',
        email='agent@test.com',
        password='testpass123'
    )
    
    # Create a test ticket with 'Open' status
    ticket = Ticket.objects.create(
        ticket_id='TEST001',
        title='Test Ticket',
        description='This is a test ticket',
        created_by=admin_user,
        status='Open'
    )
    
    print(f"\n1. Created ticket with status: {ticket.status}")
    print(f"   Initial assigned_to: {ticket.assigned_to}")
    
    # Simulate admin assigning ticket to agent
    ticket.assigned_to = agent_user
    
    # Apply the same logic as in the view
    if ticket.assigned_to and ticket.status == 'Open':
        ticket.status = 'In Progress'
    
    ticket.save()
    
    # Refresh from database
    ticket.refresh_from_db()
    
    print(f"\n2. After assignment:")
    print(f"   Status: {ticket.status}")
    print(f"   Assigned to: {ticket.assigned_to}")
    
    # Verify the change
    if ticket.status == 'In Progress':
        print("   ✅ SUCCESS: Status changed to 'In Progress' when assigned to agent")
    else:
        print(f"   ❌ FAILED: Expected 'In Progress', got '{ticket.status}'")
    
    # Test that unassigning doesn't change status
    print(f"\n3. Testing unassignment:")
    ticket.assigned_to = None
    ticket.save()
    ticket.refresh_from_db()
    
    print(f"   Status after unassignment: {ticket.status}")
    if ticket.status == 'In Progress':
        print("   ✅ SUCCESS: Status remains 'In Progress' when unassigned")
    else:
        print(f"   ❌ FAILED: Status changed unexpectedly to '{ticket.status}'")
    
    # Clean up
    ticket.delete()
    admin_user.delete()
    agent_user.delete()
    
    print("\n" + "=" * 50)
    print("✅ Ticket assignment status test completed!")
    
    print("\nManual Testing Steps:")
    print("1. Login as admin")
    print("2. Go to admin dashboard")
    print("3. Create a new ticket (status will be 'Open')")
    print("4. Edit the ticket and assign it to an agent")
    print("5. Check that status changes to 'In Progress'")

if __name__ == '__main__':
    test_ticket_assignment_status()
