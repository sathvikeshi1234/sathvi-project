#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

print('=== COMPREHENSIVE ADMIN SIGNUP AND LOGIN CHECK ===')

# Test 1: Check views exist
print('\n1. CHECKING VIEWS:')
try:
    from superadmin.views import admin_signup, superadmin_login
    print('OK admin_signup view imported')
    print('OK superadmin_login view imported')
except Exception as e:
    print(f'ERROR importing views: {e}')

# Test 2: Check URLs
print('\n2. CHECKING URLS:')
try:
    from django.urls import reverse
    signup_url = reverse('superadmin:admin_signup')
    login_url = reverse('superadmin:superadmin_login')
    print(f'OK Admin Signup URL: {signup_url}')
    print(f'OK Admin Login URL: {login_url}')
except Exception as e:
    print(f'ERROR URL resolution: {e}')

# Test 3: Test admin signup functionality
print('\n3. TESTING ADMIN SIGNUP:')
try:
    from django.test import Client
    import random
    
    client = Client()
    
    # Test GET request
    response = client.get('/superadmin/admin-signup/')
    print(f'GET signup page: {response.status_code}')
    
    if response.status_code == 200:
        print('OK Signup page accessible')
        
        # Test POST request with unique data
        unique_username = f'TestAdmin{random.randint(1000, 9999)}'
        signup_data = {
            'username': unique_username,
            'email': f'{unique_username}@test.com',
            'password': 'TestPass123!',
            'confirm_password': 'TestPass123!'
        }
        
        response = client.post('/superadmin/admin-signup/', data=signup_data)
        print(f'POST signup request: {response.status_code}')
        
        if response.status_code == 302:
            print('OK Admin signup successful - redirecting')
            redirect_url = response.get('Location')
            print(f'Redirecting to: {redirect_url}')
        elif response.status_code == 200:
            print('ERROR Form returned - checking for errors')
            content = response.content.decode()
            
            # Look for error messages
            if 'alert' in content.lower():
                print('ERROR Error messages found:')
                lines = content.split('\n')
                for line in lines:
                    if 'alert' in line.lower() and ('error' in line.lower() or 'danger' in line.lower()):
                        print(f'  {line.strip()[:100]}')
            else:
                print('ERROR No clear error messages visible')
        else:
            print(f'ERROR Unexpected status: {response.status_code}')
    else:
        print('ERROR Cannot access signup page')
        
except Exception as e:
    print(f'ERROR testing signup: {e}')

# Test 4: Test admin login functionality
print('\n4. TESTING ADMIN LOGIN:')
try:
    from django.contrib.auth.models import User
    
    # Find existing admin user
    admin_user = User.objects.filter(username='TestSathvika').first()
    if admin_user:
        print(f'OK Found admin user: {admin_user.username}')
        
        # Test login
        login_data = {
            'username': 'TestSathvika',
            'password': 'TestPass123!'
        }
        
        response = client.post('/superadmin/login/', data=login_data)
        print(f'POST login request: {response.status_code}')
        
        if response.status_code == 302:
            print('OK Admin login successful - redirecting')
            redirect_url = response.get('Location')
            print(f'Redirecting to: {redirect_url}')
            
            # Test dashboard access
            dashboard_response = client.get(redirect_url)
            print(f'Dashboard access: {dashboard_response.status_code}')
            
            if dashboard_response.status_code == 200:
                content = dashboard_response.content.decode()
                if 'paymentRequiredModal' in content:
                    print('OK Payment modal found in dashboard')
                else:
                    print('INFO No payment modal (trial may be active)')
        else:
            print('ERROR Login failed')
    else:
        print('ERROR No admin user found - TestSathvika')
        
except Exception as e:
    print(f'ERROR testing login: {e}')

print('\n=== MANUAL TESTING INSTRUCTIONS ===')
print('1. ADMIN SIGNUP:')
print('   URL: http://127.0.0.1:8000/superadmin/admin-signup/')
print('   Fill: Username, Email, Password, Confirm Password')
print('   Submit: Should redirect to login page')

print('\n2. ADMIN LOGIN:')
print('   URL: http://127.0.0.1:8000/superadmin/login/')
print('   Credentials: TestSathvika / TestPass123!')
print('   Expected: Dashboard with payment modal (if trial expired)')

print('\n3. DEBUG TIPS:')
print('   - Open browser console (F12) for JavaScript errors')
print('   - Check Network tab for form submissions')
print('   - Look for error messages in page content')
print('   - Verify Django server is running')

print('\n=== URL SUMMARY ===')
print('Admin Signup: http://127.0.0.1:8000/superadmin/admin-signup/')
print('Admin Login:  http://127.0.0.1:8000/superadmin/login/')
print('Admin Dashboard: http://127.0.0.1:8000/superadmin/dashboard/')
