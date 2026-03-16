#!/usr/bin/env python3
"""
Check the charts without unicode characters
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

def check_charts_simple():
    print("Checking Charts Simple")
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
        
        # Check for chart containers
        print("\nChart Containers:")
        print("-" * 30)
        
        chart_containers = [
            'tickets-overview-chart',
            'ticket-status-chart', 
            'tickets-by-priority-chart',
            'tickets-by-channel-chart'
        ]
        
        for container in chart_containers:
            if f'id="{container}"' in content:
                print(f"OK {container}: Found")
            else:
                print(f"MISSING {container}: Missing")
        
        # Check for Chart.js
        if 'chart.js' in content:
            print("OK Chart.js library: Found")
        else:
            print("MISSING Chart.js library: Missing")
        
        # Check for initializeCharts function
        if 'function initializeCharts()' in content:
            print("OK initializeCharts function: Found")
        else:
            print("MISSING initializeCharts function: Missing")
        
        # Check if charts are being initialized
        if 'new Chart(' in content:
            chart_count = content.count('new Chart(')
            print(f"OK Chart instantiations: {chart_count} found")
        else:
            print("MISSING No Chart instantiations found")
        
        # Check for DOM ready
        if 'DOMContentLoaded' in content:
            print("OK DOM ready event found")
        else:
            print("MISSING DOM ready event missing")
        
        # Look for potential issues
        print("\nLooking for issues:")
        print("-" * 30)
        
        # Check if there are any JavaScript errors in the template
        if 'JSON.parse' in content:
            print("OK JSON parsing is being used")
        else:
            print("ISSUE No JSON parsing found")
            
        # Check for canvas elements
        if '<canvas' in content:
            canvas_count = content.count('<canvas')
            print(f"OK Canvas elements: {canvas_count} found")
        else:
            print("ISSUE No canvas elements found")
        
        # Save the content to a file for manual inspection
        with open('debug_reports.html', 'w', encoding='utf-8') as f:
            f.write(content)
        print("DEBUG: Saved content to debug_reports.html for inspection")
            
    else:
        print(f"Error: {response.status_code}")

if __name__ == "__main__":
    check_charts_simple()
