#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User
from users.models import UserProfile, Role

print('=== Comprehensive Admin Signup Test ===')

client = Client()

# Test 1: Check if admin user was actually created
print('Test 1: Check if admin user was created')
try:
    test_admin = User.objects.get(username='testadmin123')
    print(f'✅ Test admin user found: {test_admin.username}')
    
    # Check if profile exists
    try:
        profile = test_admin.userprofile
        print(f'✅ Profile exists: {profile.role.name if profile.role else "No role"}')
        
        # Check if role is Admin
        if profile.role and profile.role.name == 'Admin':
            print('✅ Role correctly assigned as Admin')
        else:
            print(f'❌ Role is: {profile.role.name if profile.role else "None"}')
            
    except UserProfile.DoesNotExist:
        print('❌ No profile found for test admin')
        
except User.DoesNotExist:
    print('❌ Test admin user not found')

print()

# Test 2: Try creating a new admin user via form
print('Test 2: Create new admin user via form')
form_data = {
    'username': 'newadmin456',
    'email': 'newadmin456@example.com',
    'password': 'NewAdminPass123!',
    'confirm_password': 'NewAdminPass123!'
}

try:
    response = client.post(reverse('superadmin:admin_signup'), data=form_data)
    print(f'Form submission status: {response.status_code}')
    
    if response.status_code == 302:
        print('✅ Form submission successful (redirect)')
        
        # Check if user was created
        try:
            new_admin = User.objects.get(username='newadmin456')
            print(f'✅ New admin user created: {new_admin.username}')
            
            # Check profile and role
            try:
                profile = new_admin.userprofile
                print(f'✅ Profile created: {profile.role.name if profile.role else "No role"}')
                
                if profile.role and profile.role.name == 'Admin':
                    print('✅ Role correctly assigned as Admin')
                    print('✅ Admin signup is working!')
                else:
                    print(f'❌ Role is: {profile.role.name if profile.role else "None"}')
                    
            except UserProfile.DoesNotExist:
                print('❌ No profile created for new admin')
                
        except User.DoesNotExist:
            print('❌ New admin user not found in database')
            
    else:
        print(f'❌ Form submission failed with status: {response.status_code}')
        print(f'Response content: {response.content[:500]}')
        
except Exception as e:
    print(f'❌ Form submission error: {e}')

print()

# Test 3: Check current admin users
print('Test 3: Check current admin users')
admin_role = Role.objects.filter(name='Admin').first()
if admin_role:
    admin_users = UserProfile.objects.filter(role=admin_role)
    print(f'Current admin users: {admin_users.count()}')
    
    for profile in admin_users:
        user = profile.user
        print(f'  - {user.username} ({user.email}) - Created: {user.date_joined}')
        
        # Check if user can login
        if user.is_active:
            print(f'    ✅ Active - Staff: {user.is_staff}')
        else:
            print(f'    ❌ Inactive - Staff: {user.is_staff}')

print()

# Test 4: Check URL patterns
print('Test 4: Verify URL configuration')
try:
    from django.urls import get_resolver
    resolver = get_resolver()
    
    # Test admin signup URL
    resolved = resolver.resolve('/admin-signup/')
    if resolved:
        print(f'✅ /admin-signup/ resolves to: {resolved.view_name}')
    else:
        print('❌ /admin-signup/ does not resolve')
        
    # Test superadmin signup URL
    resolved_super = resolver.resolve('/admin-signup/signup/')
    if resolved_super:
        print(f'✅ /admin-signup/signup/ resolves to: {resolved_super.view_name}')
    else:
        print('❌ /admin-signup/signup/ does not resolve')
        
except Exception as e:
    print(f'❌ URL resolution error: {e}')

print()

# Test 5: Check template rendering
print('Test 5: Check template rendering')
try:
    from django.template.loader import render_to_string
    from superadmin.views import admin_signup
    
    # Mock request
    class MockRequest:
        def __init__(self):
            self.method = 'GET'
            self.POST = {}
            self.user = None
            self.META = {}
    
    mock_request = MockRequest()
    
    try:
        response = admin_signup(mock_request)
        print(f'✅ Template renders successfully')
        
        # Check if form action is correct
        if 'action="/superadmin/admin-signup/"' in response.content.decode():
            print('✅ Form action is correct')
        else:
            print('❌ Form action is incorrect')
            
    except Exception as e:
        print(f'❌ Template rendering error: {e}')

except Exception as e:
    print(f'❌ Template loader error: {e}')

print()
print('=== Summary ===')
print('If admin signup is still not working:')
print('1. Check browser console for JavaScript errors')
print('2. Check network tab for failed requests')
print('3. Verify you are accessing: http://127.0.0.1:8000/admin-signup/')
print('4. Try the test data above in the browser form')
print('5. Check if you get redirected to login page after submission')
