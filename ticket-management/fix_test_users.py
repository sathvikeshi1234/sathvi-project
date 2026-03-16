#!/usr/bin/env python
"""
Fix test users with correct roles
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

from django.contrib.auth.models import User
from users.models import UserProfile, Role

def fix_test_users():
    """Fix test users with correct roles and permissions"""
    print("FIXING TEST USERS")
    print("=" * 50)
    
    # Create roles
    admin_role, created = Role.objects.get_or_create(name='admin')
    user_role, created = Role.objects.get_or_create(name='user')
    agent_role, created = Role.objects.get_or_create(name='agent')
    
    print(f"Roles: admin={admin_role}, user={user_role}, agent={agent_role}")
    
    # Fix admin user
    admin_user = User.objects.filter(username='testadmin').first()
    if admin_user:
        print(f"\nFixing admin user: {admin_user}")
        admin_user.is_superuser = True
        admin_user.is_staff = True
        admin_user.save()
        
        # Update profile
        profile, created = UserProfile.objects.get_or_create(user=admin_user)
        profile.role = admin_role
        profile.save()
        
        print(f"  is_superuser: {admin_user.is_superuser}")
        print(f"  is_staff: {admin_user.is_staff}")
        print(f"  role: {profile.role}")
    
    # Fix regular user
    regular_user = User.objects.filter(username='testuser').first()
    if regular_user:
        print(f"\nFixing regular user: {regular_user}")
        regular_user.is_superuser = False
        regular_user.is_staff = False
        regular_user.save()
        
        # Update profile
        profile, created = UserProfile.objects.get_or_create(user=regular_user)
        profile.role = user_role
        profile.save()
        
        print(f"  is_superuser: {regular_user.is_superuser}")
        print(f"  is_staff: {regular_user.is_staff}")
        print(f"  role: {profile.role}")
    
    # Fix agent user
    agent_user = User.objects.filter(username='testagent').first()
    if agent_user:
        print(f"\nFixing agent user: {agent_user}")
        agent_user.is_superuser = False
        agent_user.is_staff = True  # Agents are staff
        agent_user.save()
        
        # Update profile
        profile, created = UserProfile.objects.get_or_create(user=agent_user)
        profile.role = agent_role
        profile.save()
        
        print(f"  is_superuser: {agent_user.is_superuser}")
        print(f"  is_staff: {agent_user.is_staff}")
        print(f"  role: {profile.role}")
    
    print("\n" + "=" * 50)
    print("TEST USERS FIXED")
    print("\nUser credentials:")
    print("Admin: username=testadmin, password=testpass123")
    print("User: username=testuser, password=testpass123")
    print("Agent: username=testagent, password=testpass123")

if __name__ == "__main__":
    fix_test_users()
