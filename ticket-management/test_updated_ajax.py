#!/usr/bin/env python3
"""
Test the updated AJAX ticket submission with debug logging
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User
import json

def test_updated_ajax():
    print("Testing Updated AJAX Ticket Submission")
    print("=" * 50)
    
    client = Client()
    
    # Create test user
    try:
        user = User.objects.create_user(
            username='testuser_updated',
            email='updated@example.com',
            password='testpass123'
        )
        print("Test user created")
    except:
        user = User.objects.get(username='testuser_updated')
        print("Using existing user")
    
    client.force_login(user)
    
    # Test access to dashboard ticket page
    print("\n1. Testing dashboard ticket page access...")
    dashboard_ticket_url = reverse('dashboards:user_dashboard_page', kwargs={'page': 'ticket'})
    response = client.get(dashboard_ticket_url)
    
    if response.status_code == 200:
        print("   SUCCESS: Page accessible")
        content = response.content.decode('utf-8')
        
        if 'console.log' in content:
            print("   SUCCESS: Debug logging added")
        if 'fetch(window.location.href)' in content:
            print("   SUCCESS: Using current URL for fetch")
    else:
        print(f"   FAILED: Status {response.status_code}")
        return
    
    # Test AJAX submission with valid data
    print("\n2. Testing AJAX submission with valid data...")
    ticket_data = {
        'title': 'Updated AJAX Test Ticket',
        'description': 'This is a test ticket with the updated AJAX implementation.',
        'priority': 'High',
        'category': 'Technical',
    }
    
    # Get CSRF token
    csrf_response = client.get(dashboard_ticket_url)
    csrf_token = csrf_response.cookies.get('csrftoken', '')
    if csrf_token:
        ticket_data['csrfmiddlewaretoken'] = csrf_token
    
    # Submit via AJAX
    response = client.post(
        dashboard_ticket_url,
        ticket_data,
        HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        HTTP_ACCEPT='application/json'
    )
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        try:
            json_response = json.loads(response.content.decode('utf-8'))
            print(f"   Response: {json_response}")
            
            if json_response.get('success'):
                print("   SUCCESS: AJAX submission worked!")
                print(f"   Message: {json_response.get('message')}")
                
                # Check database
                from tickets.models import Ticket
                tickets = Ticket.objects.filter(
                    created_by=user,
                    title='Updated AJAX Test Ticket'
                )
                
                if tickets.exists():
                    ticket = tickets.first()
                    print(f"   SUCCESS: Ticket found in database: ID {ticket.id}")
                else:
                    print("   WARNING: Ticket not found in database")
            else:
                print(f"   FAILED: {json_response.get('error')}")
                if 'errors' in json_response:
                    print(f"   Validation errors: {json_response['errors']}")
        except json.JSONDecodeError:
            print("   FAILED: Invalid JSON response")
            print(f"   Response content: {response.content[:300]}...")
    else:
        print(f"   FAILED: Status {response.status_code}")
        if hasattr(response, 'content'):
            print(f"   Error content: {response.content[:300]}...")
    
    print("\n" + "=" * 50)
    print("TEST COMPLETE:")
    print("Check the Django console for DEBUG messages")
    print("Open browser console for JavaScript debug messages")
    print("The form should now submit properly via AJAX")

if __name__ == '__main__':
    test_updated_ajax()
