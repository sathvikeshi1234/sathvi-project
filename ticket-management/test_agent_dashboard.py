#!/usr/bin/env python
"""
Quick test to verify agent dashboard URL routing works correctly
"""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Configure Django
django.setup()

from django.test import Client
from django.urls import reverse

def test_agent_dashboard_urls():
    """Test that agent dashboard URLs work correctly"""
    client = Client()
    
    # Test URLs that should work
    test_urls = [
        '/dashboard/agent-dashboard/tickets.html',
        '/dashboard/agent-dashboard/tickets',
        '/dashboard/agent-dashboard/reports.html',
        '/dashboard/agent-dashboard/reports',
        '/dashboard/agent-dashboard/ratings.html',
        '/dashboard/agent-dashboard/ratings',
        '/dashboard/agent-dashboard/profile.html',
        '/dashboard/agent-dashboard/profile',
        '/dashboard/agent-dashboard/settings.html',
        '/dashboard/agent-dashboard/settings',
        '/dashboard/agent-dashboard/chat.html',
        '/dashboard/agent-dashboard/chat',
    ]
    
    print("Testing Agent Dashboard URLs...")
    print("=" * 50)
    
    for url in test_urls:
        try:
            response = client.get(url)
            if response.status_code == 200:
                print(f"✅ {url} - {response.status_code}")
            elif response.status_code == 302:
                print(f"🔄 {url} - {response.status_code} (Redirect)")
            else:
                print(f"❌ {url} - {response.status_code}")
        except Exception as e:
            print(f"💥 {url} - ERROR: {e}")
    
    print("=" * 50)
    print("Test completed!")

if __name__ == '__main__':
    test_agent_dashboard_urls()
