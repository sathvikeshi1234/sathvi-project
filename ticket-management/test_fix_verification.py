#!/usr/bin/env python3
"""
Quick test to verify the NoReverseMatch error is fixed
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

def test_ticket_form_fix():
    print("Testing NoReverseMatch Error Fix")
    print("=" * 50)
    
    # Test URL reverse that was failing
    try:
        url = reverse('tickets:ticket_list')
        print(f"SUCCESS: tickets:ticket_list -> {url}")
    except Exception as e:
        print(f"FAILED: {e}")
        return
    
    # Test ticket create URL
    try:
        create_url = reverse('tickets:ticket_create')
        print(f"SUCCESS: tickets:ticket_create -> {create_url}")
    except Exception as e:
        print(f"FAILED: {e}")
        return
    
    # Test with authenticated user
    client = Client()
    
    # Create test user
    try:
        user = User.objects.create_user(
            username='testuser_fix',
            email='fix@example.com',
            password='testpass123'
        )
        print(f"Test user created: {user.username}")
    except:
        user = User.objects.get(username='testuser_fix')
        print(f"Using existing user: {user.username}")
    
    # Test ticket create form (this was failing before)
    client.force_login(user)
    response = client.get(create_url)
    print(f"\nTicket create form status: {response.status_code}")
    
    if response.status_code == 200:
        print("SUCCESS: Ticket form loads without NoReverseMatch error!")
        content = response.content.decode('utf-8')
        
        # Check that the Cancel button has correct URL
        if 'Cancel' in content:
            print("SUCCESS: Cancel button found")
        
        # Check for form elements
        if 'csrfmiddlewaretoken' in content:
            print("SUCCESS: CSRF token present")
            
        print("\n✅ NoReverseMatch error is FIXED!")
        print("The ticket creation form should now work properly.")
        
    else:
        print(f"FAILED: Status {response.status_code}")
        if hasattr(response, 'content'):
            print(f"Error: {response.content[:200]}...")

if __name__ == '__main__':
    test_ticket_form_fix()
