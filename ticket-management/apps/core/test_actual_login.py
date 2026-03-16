#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from superadmin.views import is_admin_or_superadmin

print('=== Test Actual Login Process ===')

try:
    # Find the admin user
    admin_user = User.objects.get(username='TestSathvika')
    print(f'User: {admin_user.username}')
    print(f'Can login: {is_admin_or_superadmin(admin_user)}')
    
    # Test login with Django test client
    client = Client()
    
    # Test GET request to login page
    response = client.get('/superadmin/login/')
    print(f'Login page GET: {response.status_code}')
    
    # Test POST request with credentials
    login_data = {
        'username': 'TestSathvika',
        'password': 'TestPass123!'
    }
    
    response = client.post('/superadmin/login/', data=login_data)
    print(f'Login POST status: {response.status_code}')
    
    if response.status_code == 302:
        print('SUCCESS: Login successful!')
        print(f'Redirect to: {response.get("Location")}')
        
        # Follow redirect to dashboard
        response = client.get(response.get("Location"))
        print(f'Dashboard status: {response.status_code}')
        
        if response.status_code == 200:
            print('SUCCESS: Dashboard accessible!')
            print('Payment modal should appear in the dashboard')
        else:
            print('ISSUE: Dashboard not accessible')
    else:
        print('ISSUE: Login failed')
        print(f'Response content: {response.content.decode()[:200]}')
    
except Exception as e:
    print(f'Error: {e}')
