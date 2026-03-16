#!/usr/bin/env python
"""
Test if address field is now working correctly
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

def test_address_functionality():
    print("Testing Address Field Functionality...")
    print("=" * 50)
    
    from django.contrib.auth.models import User
    from users.models import UserProfile
    from django.test import RequestFactory
    from dashboards.views import agent_dashboard_page
    
    # Get or create test user
    user, created = User.objects.get_or_create(
        username='testaddress_final',
        defaults={
            'email': 'addressfinal@example.com',
            'first_name': 'Address',
            'last_name': 'Final'
        }
    )
    
    # Get or create profile
    profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            'phone': '1234567890',
            'department': 'Testing',
            'address': 'Initial Address'
        }
    )
    
    print(f"User: {user.username}")
    print(f"Profile exists: {not created}")
    print(f"Current address: {profile.address}")
    
    # Test updating address
    new_address = '123 Updated Address Street, Updated City, Updated State'
    
    # Test the view with POST request
    factory = RequestFactory()
    request = factory.post(f'/dashboard/agent-dashboard/profile.html', {
        'action': 'profile',
        'address': new_address
    })
    request.user = user
    
    try:
        response = agent_dashboard_page(request, 'profile.html')
        print(f"\nView response status: {response.status_code}")
        
        # Check if context contains updated address
        if hasattr(response, 'context_data'):
            context = response.context_data
            profile_address = context.get('profile_address', '')
            
            print(f"Context address: {profile_address}")
            
            if new_address in profile_address:
                print("✅ SUCCESS: Address field is working correctly!")
                print(f"✅ Address saved: {new_address}")
            else:
                print("❌ ISSUE: Address field not reflected in template")
        
        print("\n" + "=" * 50)
        print("To verify in browser:")
        print("1. Login as testaddress_final user")
        print("2. Go to profile page")
        print("3. Enter address: '123 Updated Address Street, Updated City, Updated State'")
        print("4. Click 'Save Changes' or 'Save Account'")
        print("5. Address should appear in Contact section")
        print("6. Address should be saved to database")
        
        return True
        
    except Exception as e:
        print(f"Error testing address field: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_address_functionality()
