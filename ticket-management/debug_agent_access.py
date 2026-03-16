#!/usr/bin/env python
"""
Debug agent access issue
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

from django.test import Client
from django.contrib.auth.models import User
from users.models import UserProfile, Role

def debug_agent_access():
    """Debug agent access issue"""
    print("DEBUGGING AGENT ACCESS")
    print("=" * 50)
    
    # Get agent role
    agent_role = Role.objects.filter(name='agent').first()
    if agent_role:
        print(f"Agent role: {agent_role}")
    
    # Get test agent user
    agent_user = User.objects.filter(username='testagent').first()
    if agent_user:
        print(f"Found agent user: {agent_user}")
        print(f"  is_superuser: {agent_user.is_superuser}")
        print(f"  is_staff: {agent_user.is_staff}")
        print(f"  is_active: {agent_user.is_active}")
        
        # Check user profile
        if hasattr(agent_user, 'userprofile'):
            profile = agent_user.userprofile
            print(f"  Profile exists: {profile}")
            if profile.role:
                print(f"  Role: {profile.role} (name: {profile.role.name})")
            else:
                print("  No role assigned")
        else:
            print("  No user profile")
        
        # Test login
        client = Client()
        login_success = client.login(username='testagent', password='testpass123')
        print(f"  Login success: {login_success}")
        
        # Test agent dashboard access
        response = client.get('/dashboard/agent-dashboard/')
        print(f"  Agent dashboard response: {response.status_code}")
        
        if response.status_code == 302:
            print(f"  Redirect location: {response.get('Location', 'Unknown')}")
        
        # Test admin dashboard access
        response = client.get('/dashboard/admin-dashboard/')
        print(f"  Admin dashboard response: {response.status_code}")
        
        if response.status_code == 302:
            print(f"  Redirect location: {response.get('Location', 'Unknown')}")
        
        # Test the role validation functions directly
        from dashboards.views import is_admin_user, is_agent_user, is_regular_user
        
        # Create a mock request
        class MockRequest:
            def __init__(self, user):
                self.user = user
        
        mock_request = MockRequest(agent_user)
        
        print(f"  is_admin_user(): {is_admin_user(mock_request)}")
        print(f"  is_agent_user(): {is_agent_user(mock_request)}")
        print(f"  is_regular_user(): {is_regular_user(mock_request)}")
        
    else:
        print("Agent user not found")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    debug_agent_access()
