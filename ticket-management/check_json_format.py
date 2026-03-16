#!/usr/bin/env python3
"""
Check the exact JSON format being passed to the template
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

def check_json_format():
    print("Checking JSON Format")
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
        
        # Find the exact JSON being passed
        import re
        
        # Look for the status JSON in the template
        status_json_match = re.search(r'agent_report_status_percents_json.*?(\[.*?\])', content, re.DOTALL)
        if status_json_match:
            json_string = status_json_match.group(1)
            print(f"Raw JSON in template: {json_string}")
            
            # Try to parse it as JavaScript would
            try:
                # Simulate what JSON.parse() would do
                import json
                parsed = json.loads(json_string)
                print(f"Parsed JSON: {parsed}")
                print(f"Type: {type(parsed)}")
                print(f"Length: {len(parsed)}")
                
                # Check if it's the expected format
                if isinstance(parsed, list) and len(parsed) == 3:
                    print("OK: Expected format [open, resolved, inprogress]")
                    print(f"Values: Open={parsed[0]}%, Resolved={parsed[1]}%, In Progress={parsed[2]}%")
                else:
                    print(f"ISSUE: Expected list of 3 values, got {type(parsed)} with length {len(parsed)}")
                    
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
        else:
            print("Status JSON not found in template")
        
        # Also check the priority JSON
        priority_json_match = re.search(r'agent_report_priority_counts_json.*?(\[.*?\])', content, re.DOTALL)
        if priority_json_match:
            json_string = priority_json_match.group(1)
            print(f"\nPriority JSON: {json_string}")
            
            try:
                import json
                parsed = json.loads(json_string)
                print(f"Priority parsed: {parsed}")
                print(f"Type: {type(parsed)}, Length: {len(parsed)}")
            except json.JSONDecodeError as e:
                print(f"Priority JSON decode error: {e}")
        
        # Look at the JavaScript section to see how it's being used
        print("\nJavaScript Usage:")
        print("-" * 30)
        
        # Find the status chart JavaScript
        status_js_match = re.search(
            r'const statusData = JSON\.parse\(\'(.*?)\'\)',
            content
        )
        
        if status_js_match:
            js_json = status_js_match.group(1)
            print(f"JavaScript JSON.parse input: '{js_json}'")
            
            # This is what JavaScript sees
            print("JavaScript will parse this as:")
            try:
                import json
                parsed = json.loads(f'"{js_json}"')
                print(f"Result: {parsed}")
                print(f"Length: {len(parsed)}")
            except:
                print("Failed to parse")
        else:
            print("JavaScript JSON.parse not found")
            
    else:
        print(f"Error: {response.status_code}")

if __name__ == "__main__":
    check_json_format()
