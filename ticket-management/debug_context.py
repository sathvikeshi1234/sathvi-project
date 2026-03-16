#!/usr/bin/env python3
"""
Debug the context being passed to the reports template
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
from django.template import Context, Template

def debug_context():
    print("Debugging Reports Context")
    print("=" * 50)
    
    # Create client and login as agent
    client = Client()
    login_success = client.login(username='testlogin', password='test123')
    
    if not login_success:
        print("Could not login")
        return
    
    print("Logged in successfully")
    
    # Get the response
    response = client.get('/dashboard/agent-dashboard/reports.html')
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Check if the context variables are in the content
        import re
        
        # Look for actual values in the rendered content
        print("\nLooking for context variables in rendered content:")
        print("-" * 50)
        
        # Check for total tickets
        total_tickets_match = re.search(r'agent_report_total_tickets.*?(\d+)', content)
        if total_tickets_match:
            print(f"Total tickets found: {total_tickets_match.group(1)}")
        else:
            print("Total tickets NOT found")
            
        # Check for status JSON
        status_json_match = re.search(r'agent_report_status_percents_json.*?(\[.*?\])', content, re.DOTALL)
        if status_json_match:
            print(f"Status JSON found: {status_json_match.group(1)}")
        else:
            print("Status JSON NOT found")
            
        # Check for priority JSON
        priority_json_match = re.search(r'agent_report_priority_counts_json.*?(\[.*?\])', content, re.DOTALL)
        if priority_json_match:
            print(f"Priority JSON found: {priority_json_match.group(1)}")
        else:
            print("Priority JSON NOT found")
            
        # Check for channel data
        channel_email_match = re.search(r'agent_report_channel_email_count.*?(\d+)', content)
        if channel_email_match:
            print(f"Channel email count found: {channel_email_match.group(1)}")
        else:
            print("Channel email count NOT found")
        
        # Look for the actual values in the JavaScript section
        print("\nChecking JavaScript section:")
        print("-" * 50)
        
        # Look for JSON.parse calls
        json_parse_matches = re.findall(r'JSON\.parse\(\'(.*?)\'\)', content, re.DOTALL)
        for i, match in enumerate(json_parse_matches):
            print(f"JSON.parse {i+1}: {match[:100]}...")
            
        print("\n" + "=" * 50)
        print("Context debug completed!")
        
    else:
        print(f"Error: {response.status_code}")

if __name__ == "__main__":
    debug_context()
