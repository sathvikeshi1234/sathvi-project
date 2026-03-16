#!/usr/bin/env python
"""
Test role-based access control
"""
import os
import sys
import django

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client, TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from users.models import UserProfile, Role

def test_role_access():
    """Test role-based access control"""
    print("TESTING ROLE-BASED ACCESS CONTROL")
    print("=" * 50)
    
    # Create test roles if they don't exist
    admin_role, created = Role.objects.get_or_create(name='admin')
    user_role, created = Role.objects.get_or_create(name='user')
    agent_role, created = Role.objects.get_or_create(name='agent')
    
    # Create test users
    admin_user = User.objects.filter(username='testadmin').first()
    if not admin_user:
        admin_user = User.objects.create_user(
            username='testadmin',
            email='admin@test.com',
            password='testpass123'
        )
        UserProfile.objects.create(user=admin_user, role=admin_role)
    
    regular_user = User.objects.filter(username='testuser').first()
    if not regular_user:
        regular_user = User.objects.create_user(
            username='testuser',
            email='user@test.com',
            password='testpass123'
        )
        UserProfile.objects.create(user=regular_user, role=user_role)
    
    agent_user = User.objects.filter(username='testagent').first()
    if not agent_user:
        agent_user = User.objects.create_user(
            username='testagent',
            email='agent@test.com',
            password='testpass123'
        )
        UserProfile.objects.create(user=agent_user, role=agent_role)
    
    print("\n1. Testing Admin User Access:")
    client = Client()
    
    # Login as admin
    client.login(username='testadmin', password='testpass123')
    
    # Test admin dashboard access
    response = client.get('/dashboard/admin-dashboard/')
    print(f"   Admin dashboard access: {response.status_code} (should be 200)")
    
    # Test user dashboard access (should redirect)
    response = client.get('/dashboard/user-dashboard/')
    print(f"   User dashboard access: {response.status_code} (should be 302 redirect)")
    
    # Test agent dashboard access (should redirect)
    response = client.get('/dashboard/agent-dashboard/')
    print(f"   Agent dashboard access: {response.status_code} (should be 302 redirect)")
    
    print("\n2. Testing Regular User Access:")
    client = Client()
    client.login(username='testuser', password='testpass123')
    
    # Test user dashboard access
    response = client.get('/dashboard/user-dashboard/')
    print(f"   User dashboard access: {response.status_code} (should be 200)")
    
    # Test admin dashboard access (should redirect)
    response = client.get('/dashboard/admin-dashboard/')
    print(f"   Admin dashboard access: {response.status_code} (should be 302 redirect)")
    
    # Test agent dashboard access (should redirect)
    response = client.get('/dashboard/agent-dashboard/')
    print(f"   Agent dashboard access: {response.status_code} (should be 302 redirect)")
    
    print("\n3. Testing Agent User Access:")
    client = Client()
    client.login(username='testagent', password='testpass123')
    
    # Test agent dashboard access
    response = client.get('/dashboard/agent-dashboard/')
    print(f"   Agent dashboard access: {response.status_code} (should be 200)")
    
    # Test user dashboard access (should redirect)
    response = client.get('/dashboard/user-dashboard/')
    print(f"   User dashboard access: {response.status_code} (should be 302 redirect)")
    
    # Test admin dashboard access (should redirect)
    response = client.get('/dashboard/admin-dashboard/')
    print(f"   Admin dashboard access: {response.status_code} (should be 302 redirect)")
    
    print("\n4. Testing URL Direct Access:")
    
    # Test direct URL access without login
    client = Client()
    
    test_urls = [
        ('/dashboard/user-dashboard/', 'User Dashboard'),
        ('/dashboard/admin-dashboard/', 'Admin Dashboard'),
        ('/dashboard/agent-dashboard/', 'Agent Dashboard'),
    ]
    
    for url, name in test_urls:
        response = client.get(url)
        print(f"   {name} (no login): {response.status_code} (should be 302 redirect to login)")
    
    print("\n" + "=" * 50)
    print("ROLE ACCESS TEST COMPLETE")
    print("\nSECURITY STATUS:")
    print("- Admin users should only access admin dashboard")
    print("- Regular users should only access user dashboard")
    print("- Agent users should only access agent dashboard")
    print("- Unauthenticated users should be redirected to login")

if __name__ == "__main__":
    test_role_access()
