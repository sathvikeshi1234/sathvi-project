#!/usr/bin/env python
"""
Test script to verify the reports page loads correctly
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from users.models import UserProfile, Role

User = get_user_model()

def test_reports_page():
    print("Testing Reports Page...")
    
    # Get or create admin user
    admin_role, _ = Role.objects.get_or_create(name='Admin')
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@test.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        UserProfile.objects.get_or_create(user=admin_user, defaults={'role': admin_role})
    
    # Test the page
    client = Client()
    client.force_login(admin_user)
    
    # Test reports page
    response = client.get('/dashboard/admin-dashboard/reports.html/')
    print(f"Page Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("[SUCCESS] Reports page loads successfully!")
        
        # Check for key content
        content = response.content.decode()
        if 'report_total_tickets' in content:
            print("[OK] Total tickets data found")
        if 'report_resolution_rate' in content:
            print("[OK] Resolution rate data found")
        if 'report_customer_satisfaction_avg' in content:
            print("[OK] Customer satisfaction data found")
        if 'report_agent_perf' in content:
            print("[OK] Agent performance data found")
            
        print(f"Page content length: {len(content)} characters")
        
    else:
        print(f"[ERROR] Page failed to load: {response.status_code}")
        try:
            print(f"Response: {response.content.decode()[:500]}...")
        except:
            print(f"Response: {response.content[:500]}...")

if __name__ == '__main__':
    test_reports_page()
