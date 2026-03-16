#!/usr/bin/env python3
"""
Simple test to check if agent dashboard reports have backend data
"""

import os
import sys

# Add project path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.contrib.auth.models import User
from tickets.models import Ticket
import json

def test_reports_data():
    print("Testing Agent Reports Backend Data")
    print("=" * 50)
    
    try:
        # Check if we have users and tickets
        user_count = User.objects.count()
        ticket_count = Ticket.objects.count()
        
        print(f"Users in database: {user_count}")
        print(f"Tickets in database: {ticket_count}")
        
        if user_count == 0:
            print("❌ No users found - need to create test data")
            return
        
        # Get sample data for reports
        sample_user = User.objects.first()
        print(f"\nSample user: {sample_user.username}")
        
        # Test ticket status distribution
        open_tickets = Ticket.objects.filter(status='open').count()
        resolved_tickets = Ticket.objects.filter(status='resolved').count()
        inprogress_tickets = Ticket.objects.filter(status='in_progress').count()
        
        print(f"\nTicket Status Distribution:")
        print(f"  Open: {open_tickets}")
        print(f"  Resolved: {resolved_tickets}")
        print(f"  In Progress: {inprogress_tickets}")
        
        # Test priority distribution
        low_priority = Ticket.objects.filter(priority='low').count()
        medium_priority = Ticket.objects.filter(priority='medium').count()
        high_priority = Ticket.objects.filter(priority='high').count()
        critical_priority = Ticket.objects.filter(priority='critical').count()
        
        print(f"\nTicket Priority Distribution:")
        print(f"  Low: {low_priority}")
        print(f"  Medium: {medium_priority}")
        print(f"  High: {high_priority}")
        print(f"  Critical: {critical_priority}")
        
        # Create JSON data like the backend does
        status_percents = [open_tickets, resolved_tickets, inprogress_tickets]
        priority_counts = [low_priority, medium_priority, high_priority, critical_priority]
        
        print(f"\nJSON Data for Charts:")
        print(f"Status percents JSON: {json.dumps(status_percents)}")
        print(f"Priority counts JSON: {json.dumps(priority_counts)}")
        
        # Channel data (using default values since we don't have channel field)
        channel_data = {
            'email': 15,
            'phone': 8, 
            'chat': 12,
            'web': 5
        }
        
        print(f"\nChannel Data:")
        for channel, count in channel_data.items():
            print(f"  {channel}: {count}")
        
        print("\n" + "=" * 50)
        print("✅ Backend data test completed!")
        print("📊 Charts should display this data on the reports page")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_reports_data()
