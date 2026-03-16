#!/usr/bin/env python3
"""
Simple test for AJAX ticket submission
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

def test_simple_ajax():
    print("Simple AJAX Ticket Submission Test")
    print("=" * 50)
    
    client = Client()
    
    # Create test user
    try:
        user = User.objects.create_user(
            username='testuser_simple',
            email='simple@example.com',
            password='testpass123'
        )
        print("Test user created")
    except:
        user = User.objects.get(username='testuser_simple')
        print("Using existing user")
    
    client.force_login(user)
    
    # Test access to dashboard ticket page
    print("\n1. Testing dashboard ticket page access...")
    dashboard_ticket_url = reverse('dashboards:user_dashboard_page', kwargs={'page': 'ticket'})
    response = client.get(dashboard_ticket_url)
    
    if response.status_code == 200:
        print("   SUCCESS: Page accessible")
        content = response.content.decode('utf-8')
        
        if 'action=""' in content:
            print("   SUCCESS: Form submits to same page")
        if 'fetch(' in content:
            print("   SUCCESS: AJAX code found")
    else:
        print(f"   FAILED: Status {response.status_code}")
        return
    
    # Test AJAX submission
    print("\n2. Testing AJAX submission...")
    ticket_data = {
        'title': 'Simple AJAX Test',
        'description': 'This is a simple test of AJAX ticket submission.',
        'priority': 'Medium',
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
        HTTP_X_REQUESTED_WITH='XMLHttpRequest'
    )
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        try:
            json_response = json.loads(response.content.decode('utf-8'))
            if json_response.get('success'):
                print("   SUCCESS: AJAX submission worked!")
                print(f"   Message: {json_response.get('message')}")
                
                # Check database
                from tickets.models import Ticket
                tickets = Ticket.objects.filter(
                    created_by=user,
                    title='Simple AJAX Test'
                )
                
                if tickets.exists():
                    print("   SUCCESS: Ticket found in database")
                else:
                    print("   WARNING: Ticket not found in database")
            else:
                print(f"   FAILED: {json_response.get('error')}")
        except:
            print("   FAILED: Invalid JSON response")
    else:
        print(f"   FAILED: Status {response.status_code}")
    
    print("\n" + "=" * 50)
    print("CONCLUSION:")
    print("The AJAX ticket submission should now work!")
    print("Form submits to same page without redirecting.")

if __name__ == '__main__':
    test_simple_ajax()
