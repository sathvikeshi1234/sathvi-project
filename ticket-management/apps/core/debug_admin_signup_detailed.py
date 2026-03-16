#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from django.contrib.messages import get_messages

print('=== Admin Signup Detailed Debug ===')

# Create a test client
client = Client()

# Test 1: Direct URL access
print('Test 1: Direct URL access')
try:
    url = reverse('superadmin:admin_signup')
    print(f'URL: {url}')
    
    response = client.get(url)
    print(f'Status: {response.status_code}')
    print(f'Content type: {response.get("Content-Type")}')
    
    if response.status_code == 200:
        print('✅ URL accessible')
        print(f'Template used: {response.templates}')
        
        # Check if form is in response
        if 'form' in response.content.decode():
            print('✅ Form found in response')
        else:
            print('❌ Form NOT found in response')
    else:
        print(f'❌ URL returned {response.status_code}')
        
except Exception as e:
    print(f'❌ URL test error: {e}')

print()

# Test 2: Check template rendering
print('Test 2: Template rendering check')
try:
    from django.template.loader import render_to_string
    from superadmin.views import admin_signup
    
    # Simulate a GET request
    class MockRequest:
        def __init__(self):
            self.method = 'GET'
            self.POST = {}
            self.user = None
            self.META = {}
    
    mock_request = MockRequest()
    
    try:
        response = admin_signup(mock_request)
        print(f'Template render status: {response.status_code}')
        
        # Check if template file exists
        import os
        template_path = os.path.join('templates', 'superadmin', 'admin_signup.html')
        if os.path.exists(template_path):
            print(f'✅ Template file exists: {template_path}')
        else:
            print(f'❌ Template file missing: {template_path}')
            
    except Exception as e:
        print(f'❌ Template render error: {e}')
        
except Exception as e:
    print(f'❌ Template test error: {e}')

print()

# Test 3: Check form submission
print('Test 3: Form submission test')
try:
    url = reverse('superadmin:admin_signup')
    
    # Test with valid data
    form_data = {
        'username': 'testadmin789',
        'email': 'testadmin789@example.com',
        'password': 'TestPass123!',
        'confirm_password': 'TestPass123!'
    }
    
    response = client.post(url, data=form_data)
    print(f'POST status: {response.status_code}')
    
    if response.status_code == 302:
        print('✅ Form submission successful (redirect)')
        print(f'Redirect location: {response.get("Location")}')
    elif response.status_code == 200:
        print('⚠️ Form returned to same page (validation error)')
        # Check for error messages
        messages = list(get_messages(response.wsgi_request))
        if messages:
            for message in messages:
                print(f'Error message: {message.message}')
    else:
        print(f'❌ Unexpected status: {response.status_code}')
        
except Exception as e:
    print(f'❌ Form submission error: {e}')

print()

# Test 4: Check static files
print('Test 4: Static files check')
try:
    from django.contrib.staticfiles import finders
    static_files = finders.find('admin_signup.html')
    if static_files:
        print(f'Static files found: {static_files}')
    else:
        print('No static files for admin_signup.html')
        
except Exception as e:
    print(f'Static files check error: {e}')

print()

# Test 5: Check URL patterns
print('Test 5: URL pattern verification')
try:
    from django.urls import get_resolver
    resolver = get_resolver()
    
    # Test admin signup URL resolution
    resolved = resolver.resolve('/admin-signup/')
    if resolved:
        print(f'✅ URL resolves to: {resolved.view_name}')
        print(f'URL namespace: {resolved.namespace}')
    else:
        print('❌ URL does not resolve')
        
except Exception as e:
    print(f'❌ URL resolution error: {e}')

print('\n=== Common Issues Checklist ===')
print('1. Template file exists and is accessible')
print('2. URL routing is correct')
print('3. Form action is pointing to correct URL')
print('4. No JavaScript errors blocking submission')
print('5. No CSS conflicts preventing form display')
print('6. Server is running and accessible')
print('7. No middleware blocking the request')

print('\n=== Next Debug Steps ===')
print('1. Open browser dev tools (F12)')
print('2. Go to: http://127.0.0.1:8000/admin-signup/')
print('3. Check Network tab for failed requests')
print('4. Check Console for JavaScript errors')
print('5. Check Response headers')
print('6. Try submitting with different browsers')
