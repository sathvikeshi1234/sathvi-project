#!/usr/bin/env python3
"""
Test agent dashboard reports data
"""

import os
import sys
import django

# Add project path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.dashboards.views import agent_dashboard_page
from django.test import RequestFactory
from django.contrib.auth.models import User

def test_agent_reports():
    print("Testing Agent Dashboard Reports Data")
    print("=" * 50)
    
    # Create a mock request
    factory = RequestFactory()
    user = User.objects.first()  # Get any user for testing
    if not user:
        print("No users found in database")
        return
    
    request = factory.get('/dashboard/agent-dashboard/reports.html')
    request.user = user
    
    try:
        # Get the response
        response = agent_dashboard_page(request, 'reports.html')
        
        # Check if response has context data
        if hasattr(response, 'context_data'):
            context = response.context_data
        else:
            print("Response doesn't have context_data")
            return
        
        print("Backend data available:")
        print("-" * 40)
        
        # Check key data points
        data_points = [
            'agent_report_overview_months_json',
            'agent_report_status_percents_json', 
            'agent_report_priority_counts_json',
            'agent_report_channel_email_count',
            'agent_report_channel_phone_count',
            'agent_report_channel_chat_count',
            'agent_report_channel_web_count',
            'agent_report_total_tickets',
            'agent_report_user_name'
        ]
        
        for data_point in data_points:
            value = context.get(data_point, 'NOT FOUND')
            print(f"{data_point}: {value}")
        
        print("\n" + "=" * 50)
        print("✅ Agent dashboard reports data test completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_agent_reports()
