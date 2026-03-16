#!/usr/bin/env python3
"""
Debug the ticket status chart specifically
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

def debug_status_chart():
    print("Debugging Ticket Status Chart")
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
        
        # Check the ticket status chart section
        print("\nTicket Status Chart Section:")
        print("-" * 40)
        
        # Find the status chart section
        import re
        
        # Look for the status chart container and its context
        status_section_match = re.search(
            r'<div class="card-header">\s*<h5 class="mb-0">Ticket Status</h5>.*?</div>.*?<div class="card-body d-flex flex-column">(.*?)</div>',
            content, 
            re.DOTALL
        )
        
        if status_section_match:
            section_content = status_section_match.group(1)
            print("Found ticket status section")
            
            # Check if canvas is there
            if '<canvas id="ticket-status-chart"' in section_content:
                print("OK Canvas element found")
            else:
                print("ISSUE Canvas element missing")
            
            # Check if the legend data is there
            if 'agent_report_open_percent' in section_content:
                print("OK Legend data found")
            else:
                print("ISSUE Legend data missing")
        else:
            print("ISSUE Ticket status section not found")
        
        # Check the JavaScript for status chart
        print("\nJavaScript Status Chart:")
        print("-" * 40)
        
        # Look for the status chart JavaScript code
        status_js_match = re.search(
            r'// Ticket Status Chart.*?const statusCtx.*?new Chart\(statusCtx.*?}\);',
            content,
            re.DOTALL
        )
        
        if status_js_match:
            print("OK Status chart JavaScript found")
            
            # Extract the data being used
            js_code = status_js_match.group(0)
            
            # Look for the statusData variable
            status_data_match = re.search(r'const statusData = JSON\.parse\(\'(.*?)\'\)', js_code)
            if status_data_match:
                status_data = status_data_match.group(1)
                print(f"Status data: {status_data}")
                
                # Parse the JSON to see the actual values
                try:
                    import json
                    parsed_data = json.loads(f'"{status_data}"')
                    print(f"Parsed status data: {parsed_data}")
                    
                    # Check if the data makes sense
                    if len(parsed_data) == 3:
                        print(f"Open: {parsed_data[0]}%, Resolved: {parsed_data[1]}%, In Progress: {parsed_data[2]}%")
                    else:
                        print(f"ISSUE Expected 3 values, got {len(parsed_data)}")
                        
                except json.JSONDecodeError as e:
                    print(f"ISSUE JSON decode error: {e}")
            else:
                print("ISSUE Status data variable not found")
        else:
            print("ISSUE Status chart JavaScript not found")
        
        # Check if there are any JavaScript errors
        print("\nJavaScript Errors:")
        print("-" * 40)
        
        # Look for console.log statements or errors
        if 'console.error' in content:
            print("Found console.error statements")
        
        # Check if the chart is being created properly
        if 'new Chart(statusCtx' in content:
            print("OK Chart creation found")
        else:
            print("ISSUE Chart creation not found")
            
    else:
        print(f"Error: {response.status_code}")

if __name__ == "__main__":
    debug_status_chart()
