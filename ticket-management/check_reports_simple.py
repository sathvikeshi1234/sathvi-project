#!/usr/bin/env python3
"""
Simple check of agent dashboard reports page
"""

import os
import sys

# Add project path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.test import Client
from django.contrib.auth import authenticate

def check_reports_page():
    print("Checking Agent Dashboard Reports Page")
    print("=" * 50)
    
    # Create client and login as agent
    client = Client()
    
    # Try to login as test user
    login_success = client.login(username='testlogin', password='test123')
    if not login_success:
        # Try another user
        login_success = client.login(username='arikatlasathvika', password='testpass123')
    
    if not login_success:
        print("Could not login with test users")
        return
    
    print("Logged in successfully")
    
    # Test the reports page
    response = client.get('/dashboard/agent-dashboard/reports.html')
    
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Check for key elements
        checks = [
            ('Chart.js CDN', 'chart.js' in content),
            ('Tickets Overview Chart', 'tickets-overview-chart' in content),
            ('Ticket Status Chart', 'ticket-status-chart' in content),
            ('Priority Chart', 'tickets-by-priority-chart' in content),
            ('Channel Chart', 'tickets-by-channel-chart' in content),
            ('Backend Data - Status', 'agent_report_status_percents_json' in content),
            ('Backend Data - Priority', 'agent_report_priority_counts_json' in content),
            ('Backend Data - Channel', 'agent_report_channel_email_count' in content),
            ('initializeCharts function', 'initializeCharts()' in content),
        ]
        
        print("\nPage Content Analysis:")
        print("-" * 40)
        for check_name, found in checks:
            status = "OK" if found else "MISSING"
            print(f"{status}: {check_name}")
        
        # Check if there are actual data values
        print(f"\nBackend Data Values:")
        print("-" * 40)
        
        # Look for actual data values in the content
        import re
        
        # Find status percents
        status_match = re.search(r'agent_report_status_percents_json.*?(\[.*?\])', content)
        if status_match:
            print(f"Status data: {status_match.group(1)}")
        
        # Find priority counts
        priority_match = re.search(r'agent_report_priority_counts_json.*?(\[.*?\])', content)
        if priority_match:
            print(f"Priority data: {priority_match.group(1)}")
        
        # Find channel data
        channel_email_match = re.search(r'agent_report_channel_email_count.*?(\d+)', content)
        if channel_email_match:
            print(f"Channel email count: {channel_email_match.group(1)}")
        
        # Check for JavaScript errors
        if 'JSON.parse' in content:
            print("JavaScript JSON parsing found")
        else:
            print("No JSON parsing found - potential issue")
        
        print("\n" + "=" * 50)
        print("Reports page check completed!")
        
    else:
        print(f"Error accessing reports page: {response.status_code}")
        if hasattr(response, 'content'):
            print(f"Error content: {response.content.decode('utf-8')[:200]}...")

if __name__ == "__main__":
    check_reports_page()
