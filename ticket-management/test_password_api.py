#!/usr/bin/env python
"""
Test script to verify the SetUserPasswordView API endpoint
"""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import RequestFactory
from apps.users.views import SetUserPasswordView
from django.contrib.auth import get_user_model

User = get_user_model()

def test_set_password_api():
    """Test the set password API endpoint"""
    
    # Create a test user if it doesn't exist
    test_user, created = User.objects.get_or_create(
        username='test_agent',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'Agent',
            'is_staff': True
        }
    )
    
    if created:
        test_user.set_password('temp_password')
        test_user.save()
        print(f"Created test user: {test_user.username}")
    else:
        print(f"Using existing test user: {test_user.username}")
    
    # Create an admin user for testing
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'is_superuser': True,
            'is_staff': True
        }
    )
    
    if created:
        admin_user.set_password('admin_password')
        admin_user.save()
        print(f"Created admin user: {admin_user.username}")
    else:
        print(f"Using existing admin user: {admin_user.username}")
    
    # Test the API view
    factory = RequestFactory()
    view = SetUserPasswordView()
    
    # Create a mock request
    request = factory.post(
        f'/api/users/{test_user.id}/set-password/',
        data={
            'password': 'new_password123',
            'confirm_password': 'new_password123'
        },
        content_type='application/json'
    )
    
    # Set the admin user as the request user
    request.user = admin_user
    
    try:
        response = view.post(request, test_user.id)
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.data}")
        
        if response.status_code == 200:
            print("✅ API endpoint is working correctly!")
            
            # Verify the password was actually changed
            test_user.refresh_from_db()
            if test_user.check_password('new_password123'):
                print("✅ Password was successfully updated!")
            else:
                print("❌ Password was not updated correctly")
        else:
            print("❌ API endpoint returned an error")
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")

if __name__ == '__main__':
    test_set_password_api()
