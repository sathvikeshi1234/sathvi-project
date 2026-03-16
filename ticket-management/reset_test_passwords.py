#!/usr/bin/env python
"""
Reset test user passwords
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

def reset_passwords():
    """Reset test user passwords"""
    print("RESETTING TEST USER PASSWORDS")
    print("=" * 50)
    
    users = ['testadmin', 'testuser', 'testagent']
    password = 'testpass123'
    
    for username in users:
        user = User.objects.filter(username=username).first()
        if user:
            user.set_password(password)
            user.save()
            print(f"Reset password for {username}")
        else:
            print(f"User {username} not found")
    
    print(f"\nAll passwords set to: {password}")
    print("\nTest the login:")
    print("1. Admin: http://127.0.0.1:8000/admin-login/")
    print("2. User: http://127.0.0.1:8000/login/")
    print("3. Agent: http://127.0.0.1:8000/agent-login/")

if __name__ == "__main__":
    reset_passwords()
