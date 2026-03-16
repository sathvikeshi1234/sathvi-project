#!/usr/bin/env python3
"""
Test the charts directly by checking the actual HTML content
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

def test_charts_direct():
    print("Testing Charts Directly")
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
                print(f"✓ {container}: Found")
            else:
                print(f"✗ {container}: Missing")
        
        # Check for Chart.js
        if 'chart.js' in content:
            print("✓ Chart.js library: Found")
        else:
            print("✗ Chart.js library: Missing")
        
        # Check for initializeCharts function
        if 'function initializeCharts()' in content:
            print("✓ initializeCharts function: Found")
        else:
            print("✗ initializeCharts function: Missing")
        
        # Check for JSON data
        print("\nJSON Data Check:")
        print("-" * 30)
        
        import re
        
        # Look for the actual JSON data in the JavaScript
        json_patterns = [
            (r'const months = JSON\.parse\(\'(.*?)\'\)', 'Months'),
            (r'const createdData = JSON\.parse\(\'(.*?)\'\)', 'Created Data'),
            (r'const resolvedData = JSON\.parse\(\'(.*?)\'\)', 'Resolved Data'),
            (r'const statusData = JSON\.parse\(\'(.*?)\'\)', 'Status Data'),
            (r'const priorityData = JSON\.parse\(\'(.*?)\'\)', 'Priority Data'),
        ]
        
        for pattern, name in json_patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                data = match.group(1)
                if data and data != '[]' and data != '[0, 0, 0]':
                    print(f"✓ {name}: {data[:50]}...")
                else:
                    print(f"✗ {name}: Empty or zeros")
            else:
                print(f"✗ {name}: Not found")
        
        # Check for channel data
        channel_match = re.search(r'const channelData = \{(.*?)\}', content, re.DOTALL)
        if channel_match:
            print(f"✓ Channel Data: {channel_match.group(1)[:50]}...")
        else:
            print("✗ Channel Data: Not found")
        
        # Check if charts are being initialized
        if 'new Chart(' in content:
            chart_count = content.count('new Chart(')
            print(f"\n✓ Chart instantiations: {chart_count} found")
        else:
            print("\n✗ No Chart instantiations found")
        
        # Look for potential JavaScript errors
        print("\nPotential Issues:")
        print("-" * 30)
        
        if 'JSON.parse' in content and 'JSON.parse' in content.count('JSON.parse') > 0:
            print("✓ JSON parsing is being used")
        
        # Check for DOM ready
        if 'DOMContentLoaded' in content:
            print("✓ DOM ready event found")
        else:
            print("✗ DOM ready event missing")
            
    else:
        print(f"Error: {response.status_code}")

if __name__ == "__main__":
    test_charts_direct()
