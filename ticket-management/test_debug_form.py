#!/usr/bin/env python3
"""
Test form submission with debug logging
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

def test_form_with_debug():
    print("Testing Form Submission with Debug Logging")
    print("=" * 60)
    
    client = Client()
    
    # Create test user
    try:
        user = User.objects.create_user(
            username='testuser_debug',
            email='debug@example.com',
            password='testpass123'
        )
        print("Test user created")
    except:
        user = User.objects.get(username='testuser_debug')
        print("Using existing user")
    
    client.force_login(user)
    
    # Test the form submission
    print("\n1. Testing form submission...")
    dashboard_ticket_url = reverse('dashboards:user_dashboard_page', kwargs={'page': 'ticket'})
    
    # Prepare form data
    ticket_data = {
        'title': 'Debug Test Ticket',
        'description': 'This is a test ticket to debug form submission issues.',
        'priority': 'High',
        'category': 'Technical',
    }
    
    # Get CSRF token
    csrf_response = client.get(dashboard_ticket_url)
    csrf_token = csrf_response.cookies.get('csrftoken', '')
    if csrf_token:
        ticket_data['csrfmiddlewaretoken'] = csrf_token
    
    print("2. Submitting form with AJAX headers...")
    response = client.post(
        dashboard_ticket_url,
        ticket_data,
        HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        HTTP_ACCEPT='application/json'
    )
    
    print(f"   Status: {response.status_code}")
    print(f"   Content type: {response.get('Content-Type')}")
    
    if response.status_code == 200:
        try:
            json_response = json.loads(response.content.decode('utf-8'))
            print(f"   Response: {json_response}")
            
            if json_response.get('success'):
                print("   SUCCESS: Form submitted via AJAX!")
                print(f"   Ticket ID: {json_response.get('ticket_id')}")
            else:
                print(f"   ERROR: {json_response.get('error')}")
        except:
            print("   ERROR: Invalid JSON response")
            print(f"   Raw response: {response.content}")
    else:
        print(f"   ERROR: HTTP {response.status_code}")
        if hasattr(response, 'content'):
            print(f"   Response: {response.content[:300]}...")
    
    print("\n" + "=" * 60)
    print("CHECK DJANGO CONSOLE FOR DEBUG MESSAGES")
    print("Open browser console for JavaScript debug messages")
    print("The form should now show detailed debug information")

if __name__ == '__main__':
    test_form_with_debug()
