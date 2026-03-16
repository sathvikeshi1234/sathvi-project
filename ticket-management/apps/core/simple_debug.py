#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

print('=== COMPREHENSIVE LOGIN DEBUG ===')
print('Follow these steps in order:\n')

# Step 1: Check Django server status
print('STEP 1: Check Django Server Status')
print('1. Make sure Django server is running:')
print('   python manage.py runserver')
print('2. Server should show: "Starting development server at http://127.0.0.1:8000/"')
print('3. If not running, start it and try again\n')

# Step 2: Check user and password
print('STEP 2: Verify User Credentials')
try:
    from django.contrib.auth.models import User
    from django.contrib.auth import authenticate
    
    user = User.objects.get(username='TestSathvika')
    print(f'OK User exists: {user.username}')
    print(f'OK Email: {user.email}')
    print(f'OK Is active: {user.is_active}')
    print(f'OK Is staff: {user.is_staff}')
    
    # Test password
    auth_result = authenticate(username='TestSathvika', password='TestPass123!')
    if auth_result:
        print('OK Password authentication works')
    else:
        print('ERROR Password authentication failed - resetting...')
        user.set_password('TestPass123!')
        user.save()
        print('OK Password reset to: TestPass123!')
        
except User.DoesNotExist:
    print('ERROR User does not exist - creating...')
    User.objects.create_user('TestSathvika', 'sathvikatest@gmail.com', 'TestPass123!')
    print('OK User created with password: TestPass123!')

print()

# Step 3: Check URL routing
print('STEP 3: Check URL Routing')
try:
    from django.urls import reverse
    login_url = reverse('superadmin:superadmin_login')
    print(f'OK Login URL resolved: {login_url}')
    print('OK Try this exact URL: http://127.0.0.1:8000/superadmin/login/')
except Exception as e:
    print(f'ERROR URL routing error: {e}')

print()

# Step 4: Test login programmatically
print('STEP 4: Test Login Programmatically')
try:
    from django.test import Client
    
    client = Client()
    
    # Get login page
    response = client.get('/superadmin/login/')
    print(f'OK Login page accessible: {response.status_code}')
    
    # Test login
    login_data = {
        'username': 'TestSathvika',
        'password': 'TestPass123!'
    }
    response = client.post('/superadmin/login/', data=login_data)
    print(f'OK Login POST status: {response.status_code}')
    
    if response.status_code == 302:
        print('OK Login successful - redirecting to dashboard')
        dashboard = client.get(response.get('Location'))
        if 'paymentRequiredModal' in dashboard.content.decode():
            print('OK Payment modal found in dashboard')
        else:
            print('ERROR No modal in dashboard')
    else:
        print('ERROR Login failed')
        
except Exception as e:
    print(f'ERROR Programmatic test failed: {e}')

print()

# Step 5: Browser debugging instructions
print('STEP 5: Browser Debugging Instructions')
print('1. Open browser: http://127.0.0.1:8000/superadmin/login/')
print('2. Open Developer Tools (F12)')
print('3. Go to Network tab')
print('4. Fill form EXACTLY:')
print('   Username: TestSathvika')
print('   Password: TestPass123!')
print('5. Click Login button')
print('6. Check Network request:')
print('   - Should show POST to /superadmin/login/')
print('   - Status should be 302 (redirect)')
print('   - If status 200, login failed')
print('7. Check Console tab for errors')

print()

# Step 6: Alternative login URLs
print('STEP 6: Try Alternative URLs')
print('If main URL not working, try:')
print('1. http://127.0.0.1:8000/superadmin/login/')
print('2. http://127.0.0.1:8000/admin-login/')
print('3. http://127.0.0.1:8000/login/')

print()

# Step 7: Clear cache and restart
print('STEP 7: Clear Cache and Restart')
print('1. Stop Django server (Ctrl+C)')
print('2. Clear browser cache (Ctrl+Shift+Delete)')
print('3. Restart Django server:')
print('   python manage.py runserver')
print('4. Try incognito/private window')

print()

print('=== QUICK TEST SUMMARY ===')
print('User: TestSathvika')
print('Password: TestPass123!')
print('URL: http://127.0.0.1:8000/superadmin/login/')
print('Expected: Login -> Dashboard -> Payment Modal')

print('\nIf still not working, run this script again and check for ERROR messages!')
