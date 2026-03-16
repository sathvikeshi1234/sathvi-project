#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

print('=== DEBUG ADMIN SIGNUP ISSUE ===')

# Test 1: Check if admin signup view exists
print('1. Checking admin signup view...')
try:
    from superadmin.views import admin_signup
    print('OK admin_signup view imported successfully')
except Exception as e:
    print(f'ERROR importing admin_signup: {e}')

# Test 2: Check URL resolution
print('\n2. Testing URL resolution...')
try:
    from django.urls import reverse
    signup_url = reverse('superadmin:admin_signup')
    print(f'OK Admin signup URL: {signup_url}')
except Exception as e:
    print(f'ERROR URL resolution: {e}')

# Test 3: Test GET request to signup page
print('\n3. Testing signup page access...')
try:
    from django.test import Client
    client = Client()
    
    response = client.get('/superadmin/admin-signup/')
    print(f'GET request status: {response.status_code}')
    
    if response.status_code == 200:
        content = response.content.decode()
        if 'csrf' in content.lower():
            print('OK CSRF token present')
        if 'form' in content.lower():
            print('OK Form found in page')
        if 'admin' in content.lower() or 'signup' in content.lower():
            print('OK Page appears to be admin signup')
    else:
        print('ERROR Unexpected status code')
        
except Exception as e:
    print(f'ERROR accessing signup page: {e}')

# Test 4: Test POST request to create admin
print('\n4. Testing admin creation...')
try:
    signup_data = {
        'username': 'TestAdmin123',
        'email': 'testadmin123@example.com',
        'password': 'AdminPass123!',
        'confirm_password': 'AdminPass123!'
    }
    
    response = client.post('/superadmin/admin-signup/', data=signup_data)
    print(f'POST request status: {response.status_code}')
    
    if response.status_code == 302:
        print('OK Admin creation successful - redirecting')
        redirect_url = response.get('Location')
        print(f'Redirecting to: {redirect_url}')
    elif response.status_code == 200:
        print('ERROR Form returned - checking for errors')
        content = response.content.decode()
        if 'error' in content.lower():
            print('ERROR Error messages found in response')
            # Extract error messages
            lines = content.split('\n')
            for line in lines:
                if 'alert' in line.lower() or 'error' in line.lower():
                    print(f'  Error: {line.strip()[:100]}')
        else:
            print('ERROR Form returned but no clear errors visible')
    else:
        print(f'ERROR Unexpected status: {response.status_code}')
        
except Exception as e:
    print(f'ERROR testing admin creation: {e}')

# Test 5: Check if user was created
print('\n5. Checking if test user was created...')
try:
    from django.contrib.auth.models import User
    from users.models import UserProfile
    from superadmin.models import Role
    
    test_user = User.objects.filter(username='TestAdmin123').first()
    if test_user:
        print(f'OK Test user found: {test_user.username}')
        print(f'  Email: {test_user.email}')
        print(f'  Is staff: {test_user.is_staff}')
        
        # Check profile
        try:
            profile = test_user.userprofile
            if profile and profile.role:
                print(f'  Role: {profile.role.name}')
            else:
                print('  No profile or role found')
        except:
            print('  Profile access error')
            
        # Check if company was created
        from superadmin.models import Company, Subscription
        company = Company.objects.filter(name='TestAdmin123 Company').first()
        if company:
            print(f'OK Company created: {company.name}')
            subscription = Subscription.objects.filter(company=company).first()
            if subscription:
                print(f'OK Subscription created: {subscription.plan.name} ({subscription.status})')
            else:
                print('ERROR No subscription found')
        else:
            print('ERROR No company created')
    else:
        print('ERROR Test user was not created')
        
except Exception as e:
    print(f'ERROR checking created user: {e}')

print('\n=== MANUAL TEST INSTRUCTIONS ===')
print('1. Open browser: http://127.0.0.1:8000/superadmin/admin-signup/')
print('2. Fill form with:')
print('   Username: TestAdmin123')
print('   Email: testadmin123@example.com')
print('   Password: AdminPass123!')
print('   Confirm: AdminPass123!')
print('3. Click submit')
print('4. Check browser console (F12) for errors')
print('5. Check network tab for request/response')

print('\n=== COMMON ISSUES ===')
print('If signup is not working:')
print('1. Check if URL is correct: /superadmin/admin-signup/')
print('2. Check browser console for JavaScript errors')
print('3. Check network tab for failed requests')
print('4. Verify Django server is running')
print('5. Check if form validation is working')
