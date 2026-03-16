#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

print('=== ADMIN SIGNUP AND LOGIN URLS ===')

# Get all URL patterns
from django.urls import get_resolver
from django.urls.resolvers import URLResolver

resolver = get_resolver()

print('\n1. SuperAdmin URLs (for Admin/SuperAdmin users):')
print('   Login: http://127.0.0.1:8000/superadmin/login/')
print('   Signup: http://127.0.0.1:8000/superadmin/admin-signup/')
print('   Alternative Signup: http://127.0.0.1:8000/superadmin/signup/')
print('   Dashboard: http://127.0.0.1:8000/superadmin/dashboard/')

print('\n2. Regular User URLs (for comparison):')
print('   Login: http://127.0.0.1:8000/login/')
print('   Admin Login: http://127.0.0.1:8000/admin-login/')
print('   Admin Signup: http://127.0.0.1:8000/admin-signup/')

print('\n3. URL Patterns from superadmin/urls.py:')
superadmin_patterns = [
    ('/superadmin/login/', 'superadmin_login', 'Admin/SuperAdmin Login'),
    ('/superadmin/admin-signup/', 'admin_signup', 'Admin/SuperAdmin Signup'),
    ('/superadmin/signup/', 'superadmin_signup', 'Admin/SuperAdmin Signup (alternative)'),
    ('/superadmin/dashboard/', 'superadmin_dashboard', 'Admin/SuperAdmin Dashboard'),
]

for pattern, view_name, description in superadmin_patterns:
    print(f'   {pattern:<35} -> {view_name:<20} ({description})')

print('\n4. URL Patterns from users/urls.py:')
user_patterns = [
    ('/login/', 'login_view', 'Regular User Login'),
    ('/admin-login/', 'admin_login_view', 'Admin Login (users app)'),
    ('/admin-signup/', 'admin_signup_view', 'Admin Signup (users app)'),
    ('/user-login/', 'user_login_view', 'Regular User Login (specific)'),
]

for pattern, view_name, description in user_patterns:
    print(f'   {pattern:<35} -> {view_name:<20} ({description})')

print('\n5. RECOMMENDED URLS FOR ADMIN USERS:')
print('   Use SuperAdmin URLs for proper trial/payment integration:')
print('   - Login: http://127.0.0.1:8000/superadmin/login/')
print('   - Signup: http://127.0.0.1:8000/superadmin/admin-signup/')

print('\n6. KEY DIFFERENCES:')
print('   SuperAdmin URLs:')
print('     - Creates trial subscription automatically')
print('     - Shows payment modal when trial expires')
print('     - Integrates with payment processing')
print('   ')
print('   Users App URLs:')
print('     - Basic login/signup without trial integration')
print('     - No payment modal functionality')

print('\n=== SUMMARY ===')
print('For Admin/SuperAdmin users, use:')
print('http://127.0.0.1:8000/superadmin/login/')
print('http://127.0.0.1:8000/superadmin/admin-signup/')
