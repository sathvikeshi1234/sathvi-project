#!/usr/bin/env python
"""
Test script to verify the settings fix works correctly
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django without running migrations
import django
from django.conf import settings
settings.DEBUG = True
django.setup()

from apps.dashboards.models import SiteSettings

def test_settings_persistence():
    print("=== Testing Settings Persistence ===")
    
    # Get current settings
    settings_obj = SiteSettings.get_solo()
    print(f"Current company_name: '{settings_obj.company_name}'")
    print(f"Current currency: '{settings_obj.currency}'")
    
    # Test changing values
    test_company = "Test Company " + str(os.getpid())  # Unique name
    test_currency = "EUR - Euro (€)"
    
    print(f"\n=== Updating settings ===")
    print(f"Setting company_name to: '{test_company}'")
    print(f"Setting currency to: '{test_currency}'")
    
    settings_obj.company_name = test_company
    settings_obj.currency = test_currency
    settings_obj.save()
    
    # Verify the changes were saved
    settings_obj.refresh_from_db()
    print(f"\n=== After save ===")
    print(f"Saved company_name: '{settings_obj.company_name}'")
    print(f"Saved currency: '{settings_obj.currency}'")
    
    # Test get_solo() returns the same object
    settings_obj2 = SiteSettings.get_solo()
    print(f"\n=== Via get_solo() ===")
    print(f"Retrieved company_name: '{settings_obj2.company_name}'")
    print(f"Retrieved currency: '{settings_obj2.currency}'")
    
    # Check if values match
    if settings_obj2.company_name == test_company and settings_obj2.currency == test_currency:
        print("\n✅ SUCCESS: Settings are persisting correctly!")
        return True
    else:
        print("\n❌ FAILURE: Settings are not persisting correctly!")
        return False

if __name__ == '__main__':
    try:
        success = test_settings_persistence()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
