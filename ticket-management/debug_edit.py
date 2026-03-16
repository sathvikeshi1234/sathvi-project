#!/usr/bin/env python
"""
Debug script to test admin ticket edit functionality
"""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth.models import User
from tickets.models import Ticket
from dashboards.views import admin_ticket_edit

def debug_admin_ticket_edit():
    print("Debugging admin ticket edit functionality...")
    
    # Try to get an existing admin user or create one
    try:
        admin_user = User.objects.filter(is_staff=True).first()
        if not admin_user:
            admin_user = User.objects.create_user(
                username='debug_admin',
                email='admin@debug.com',
                password='debugpass123',
                is_staff=True,
                is_superuser=True
            )
        print(f"+ Using admin user: {admin_user.username}")
    except Exception as e:
        print(f"- Error with admin user: {e}")
        return False
    
    # Try to get an existing ticket or create one
    try:
        ticket = Ticket.objects.first()
        if not ticket:
            ticket = Ticket.objects.create(
                title='Debug Test Ticket',
                description='This is a debug test ticket',
                priority='Medium',
                status='Open',
                created_by=admin_user
            )
        print(f"+ Using ticket: {ticket.ticket_id} (ID: {ticket.id})")
    except Exception as e:
        print(f"- Error with ticket: {e}")
        return False
    
    # Test GET request
    factory = RequestFactory()
    request = factory.get(f'/dashboard/admin-dashboard/ticket/{ticket.ticket_id}/edit/')
    request.user = admin_user
    
    try:
        print("\nTesting GET request...")
        response = admin_ticket_edit(request, ticket.ticket_id)
        print(f"+ Response status: {response.status_code}")
        
        # Check if response contains expected content
        if hasattr(response, 'content'):
            content = response.content.decode('utf-8')
            if 'ticketEditModal' in content:
                print("+ Modal found in response")
            else:
                print("- Modal NOT found in response")
                
            if 'ticket_edit' in content:
                print("+ Edit template found in response")
            else:
                print("- Edit template NOT found in response")
                
            if 'form' in content.lower():
                print("+ Form found in response")
            else:
                print("- Form NOT found in response")
                
        # Check context data
        if hasattr(response, 'context_data') and response.context_data:
            context = response.context_data
            print(f"+ Context keys: {list(context.keys())}")
            
            if 'ticket' in context:
                print(f"+ Ticket in context: {context['ticket'].title}")
            else:
                print("- Ticket NOT in context")
                
            if 'form' in context:
                print(f"+ Form in context: {type(context['form']).__name__}")
            else:
                print("- Form NOT in context")
                
            if 'agents' in context:
                agents_count = len(context['agents']) if context['agents'] else 0
                print(f"+ Agents in context: {agents_count} agents")
            else:
                print("- Agents NOT in context")
                
    except Exception as e:
        print(f"- GET request failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n+ Debug test completed successfully!")
    return True

if __name__ == '__main__':
    success = debug_admin_ticket_edit()
    if success:
        print("\n[SUCCESS] Admin ticket edit functionality appears to be working.")
        print("If you're still seeing 'could not load ticket edit form', check:")
        print("1. Browser console for JavaScript errors")
        print("2. Network tab for failed requests")
        print("3. Make sure you're logged in as admin/staff")
    else:
        print("\n[ERROR] Issues found with admin ticket edit functionality.")
        sys.exit(1)
