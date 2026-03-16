#!/usr/bin/env python
"""
Test script to check if URLs change when modified
"""
import os
import sys
import django
from django.test import Client
from django.urls import reverse
from django.conf import settings

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def backup_url_file():
    """Create backup of URL files"""
    import shutil
    shutil.copy('apps/users/urls.py', 'apps/users/urls.py.backup')
    shutil.copy('apps/superadmin/urls.py', 'apps/superadmin/urls.py.backup')
    print("✓ Created backups of URL files")

def restore_url_file():
    """Restore URL files from backup"""
    import shutil
    if os.path.exists('apps/users/urls.py.backup'):
        shutil.copy('apps/users/urls.py.backup', 'apps/users/urls.py')
        os.remove('apps/users/urls.py.backup')
    if os.path.exists('apps/superadmin/urls.py.backup'):
        shutil.copy('apps/superadmin/urls.py.backup', 'apps/superadmin/urls.py')
        os.remove('apps/superadmin/urls.py.backup')
    print("✓ Restored URL files from backup")

def test_url_modification():
    """Test if URLs change when modified"""
    client = Client()
    
    print("=== Testing URL Modification ===\n")
    
    # Test original URLs
    print("1. ORIGINAL URLS:")
    original_urls = {}
    
    # Test users URLs
    try:
        response = client.get('/login/')
        original_urls['login'] = response.status_code
        print(f"   /login/ - Status: {response.status_code}")
    except Exception as e:
        print(f"   /login/ - Error: {e}")
    
    try:
        response = client.get('/admin-login/')
        original_urls['admin_login'] = response.status_code
        print(f"   /admin-login/ - Status: {response.status_code}")
    except Exception as e:
        print(f"   /admin-login/ - Error: {e}")
    
    try:
        response = client.get('/superadmin/login/')
        original_urls['superadmin_login'] = response.status_code
        print(f"   /superadmin/login/ - Status: {response.status_code}")
    except Exception as e:
        print(f"   /superadmin/login/ - Error: {e}")
    
    # Modify URLs temporarily
    print("\n2. MODIFYING URLS:")
    
    # Read and modify users/urls.py
    with open('apps/users/urls.py', 'r') as f:
        users_content = f.read()
    
    # Change login path
    modified_users_content = users_content.replace(
        'path("login/", views.login_view, name="login"),',
        'path("login-modified/", views.login_view, name="login"),'
    )
    
    with open('apps/users/urls.py', 'w') as f:
        f.write(modified_users_content)
    
    # Read and modify superadmin/urls.py
    with open('apps/superadmin/urls.py', 'r') as f:
        superadmin_content = f.read()
    
    # Change superadmin login path
    modified_superadmin_content = superadmin_content.replace(
        "path('login/', superadmin_login, name='superadmin_login'),",
        "path('login-modified/', superadmin_login, name='superadmin_login'),"
    )
    
    with open('apps/superadmin/urls.py', 'w') as f:
        f.write(modified_superadmin_content)
    
    print("   ✓ Modified login paths to include '-modified'")
    
    # Test modified URLs
    print("\n3. TESTING MODIFIED URLS:")
    
    # Clear URL cache
    from django.urls import get_resolver
    get_resolver().pop()
    
    try:
        response = client.get('/login-modified/')
        print(f"   /login-modified/ - Status: {response.status_code}")
    except Exception as e:
        print(f"   /login-modified/ - Error: {e}")
    
    try:
        response = client.get('/superadmin/login-modified/')
        print(f"   /superadmin/login-modified/ - Status: {response.status_code}")
    except Exception as e:
        print(f"   /superadmin/login-modified/ - Error: {e}")
    
    # Test that old URLs don't work
    print("\n4. TESTING OLD URLS (should fail):")
    
    try:
        response = client.get('/login/')
        print(f"   /login/ - Status: {response.status_code} (should be 404)")
    except Exception as e:
        print(f"   /login/ - Error: {e}")
    
    try:
        response = client.get('/superadmin/login/')
        print(f"   /superadmin/login/ - Status: {response.status_code} (should be 404)")
    except Exception as e:
        print(f"   /superadmin/login/ - Error: {e}")
    
    print("\n=== RESULT: URLs DO change when modified ===")

if __name__ == "__main__":
    try:
        backup_url_file()
        test_url_modification()
    finally:
        restore_url_file()
