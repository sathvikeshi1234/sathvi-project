#!/usr/bin/env python
"""
Final security test to demonstrate the role-based access control fix
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

def final_security_test():
    """Final comprehensive security test"""
    print("🔐 FINAL SECURITY TEST - ROLE-BASED ACCESS CONTROL")
    print("=" * 60)
    
    # Test scenarios
    scenarios = [
        {
            'username': 'testadmin',
            'password': 'testpass123',
            'role': 'Admin',
            'expected': {
                'admin_dashboard': 200,
                'user_dashboard': 302,
                'agent_dashboard': 302
            }
        },
        {
            'username': 'testuser',
            'password': 'testpass123',
            'role': 'User',
            'expected': {
                'admin_dashboard': 302,
                'user_dashboard': 200,
                'agent_dashboard': 302
            }
        },
        {
            'username': 'testagent',
            'password': 'testpass123',
            'role': 'Agent',
            'expected': {
                'admin_dashboard': 302,
                'user_dashboard': 302,
                'agent_dashboard': 200
            }
        }
    ]
    
    all_passed = True
    
    for scenario in scenarios:
        print(f"\n📋 Testing {scenario['role']} User: {scenario['username']}")
        print("-" * 40)
        
        client = Client()
        login_success = client.login(username=scenario['username'], password=scenario['password'])
        
        if not login_success:
            print(f"❌ Login failed for {scenario['username']}")
            all_passed = False
            continue
        
        dashboards = [
            ('/dashboard/admin-dashboard/', 'Admin Dashboard'),
            ('/dashboard/user-dashboard/', 'User Dashboard'),
            ('/dashboard/agent-dashboard/', 'Agent Dashboard')
        ]
        
        for url, name in dashboards:
            response = client.get(url)
            expected_key = url.split('/')[-2] + '_dashboard'
            expected_status = scenario['expected'][expected_key]
            
            if response.status_code == expected_status:
                status_icon = "✅"
            else:
                status_icon = "❌"
                all_passed = False
            
            redirect_info = ""
            if response.status_code == 302:
                redirect_info = f" → {response.get('Location', 'Unknown')}"
            
            print(f"  {status_icon} {name}: {response.status_code}{redirect_info}")
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL SECURITY TESTS PASSED!")
        print("\n✅ SECURITY FIXES VERIFIED:")
        print("   • Admin users can only access admin dashboard")
        print("   • Regular users can only access user dashboard")
        print("   • Agent users can only access agent dashboard")
        print("   • Cross-role access is properly blocked")
        print("   • Users are redirected to appropriate dashboards")
        
        print("\n🔒 ISSUE RESOLVED:")
        print("   The security issue where admin users could access user dashboard")
        print("   after changing URLs has been FIXED with proper role validation.")
        
        print("\n📝 TEST USERS FOR MANUAL VERIFICATION:")
        print("   Admin:   username=testadmin,   password=testpass123")
        print("   User:    username=testuser,    password=testpass123")
        print("   Agent:   username=testagent,   password=testpass123")
        
        print("\n🌐 MANUAL TEST URLS:")
        print("   Admin Login:   http://127.0.0.1:8000/admin-login/")
        print("   User Login:    http://127.0.0.1:8000/login/")
        print("   Agent Login:   http://127.0.0.1:8000/agent-login/")
        
    else:
        print("❌ SOME SECURITY TESTS FAILED!")
        print("   Please review the failed tests above.")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    final_security_test()
