#!/usr/bin/env python
import os
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from apps.users.models import UserProfile
from apps.superadmin.models import SuperAdminSettings
from apps.users.models import Role

# Create or get test user
role, _ = Role.objects.get_or_create(name='SuperAdmin')
user, created = User.objects.get_or_create(
    username='testsuperadmin',
    defaults={
        'email': 'test@example.com',
        'first_name': 'John',
        'last_name': 'Doe'
    }
)
user.set_password('testpass123')
user.save()

# Get or create user profile
profile, _ = UserProfile.objects.get_or_create(user=user)
profile.role = role
profile.save()

# Get or create superadmin settings
settings, _ = SuperAdminSettings.objects.get_or_create(user=user)

# Create client and login
client = Client()
login_success = client.login(username='testsuperadmin', password='testpass123')
print(f"Login success: {login_success}")

# Test personal info save
print("\n=== Testing Personal Info Save ===")
personal_info_data = {
    'action': 'save_personal_info',
    'first_name': 'Jane',
    'last_name': 'Smith',
    'email': 'jane@example.com',
    'phone': '+1-555-1234567',
    'address': '123 Main St, Anytown, USA',
    'date_of_birth': '1990-05-15',
    'gender': 'F'
}

response = client.post(
    '/superadmin/profile/',
    data=json.dumps(personal_info_data),
    content_type='application/json',
    follow=True
)

print(f"Status code: {response.status_code}")
print(f"Content type: {response.get('Content-Type')}")
print(f"Response: {response.content.decode()}")

# Refresh user from database
user.refresh_from_db()
profile.refresh_from_db()

print("\n=== Updated User Data ===")
print(f"First Name: {user.first_name}")
print(f"Last Name: {user.last_name}")
print(f"Email: {user.email}")

print("\n=== Updated Profile Data ===")
print(f"Phone: {profile.phone}")
print(f"Address: {profile.address}")
print(f"Date of Birth: {profile.date_of_birth}")
print(f"Gender: {profile.gender}")

print("\n✓ Test Complete!")
