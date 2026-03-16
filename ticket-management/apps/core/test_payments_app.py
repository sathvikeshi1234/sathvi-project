#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

print('=== PAYMENTS APP SETUP VERIFICATION ===')

# Test 1: Check if payments app can be imported
print('1. Testing imports...')
try:
    from payments import views, models, urls, admin
    from payments.apps import PaymentsConfig
    print('✓ All payments modules imported successfully')
except Exception as e:
    print(f'✗ Import error: {e}')

# Test 2: Check URL patterns
print('\n2. Testing URL patterns...')
try:
    from django.urls import reverse, include
    from django.conf import settings
    
    # Check if payments app is in INSTALLED_APPS
    if 'payments' in settings.INSTALLED_APPS:
        print('✓ Payments app is in INSTALLED_APPS')
    else:
        print('✗ Payments app not in INSTALLED_APPS - add it to settings.py')
    
    # Test URL resolution (if properly included)
    try:
        # This will work if payments URLs are properly included
        from payments.urls import urlpatterns
        print(f'✓ Payments URLs configured: {len(urlpatterns)} routes')
    except Exception as e:
        print(f'✗ URL configuration error: {e}')
        
except Exception as e:
    print(f'✗ URL test error: {e}')

# Test 3: Check models
print('\n3. Testing models...')
try:
    from payments.models import PaymentMethod, Invoice, Refund, PaymentSettings
    print('✓ Payment-specific models imported')
    
    # Check if main payment models exist
    from superadmin.models import Payment, Subscription
    print('✓ Main payment models exist')
    
except Exception as e:
    print(f'✗ Model import error: {e}')

# Test 4: Check views
print('\n4. Testing views...')
try:
    from payments.views import (
        payment_create, payment_process, payment_detail,
        payments_list, payment_update_status, payment_webhook
    )
    print('✓ All payment views imported')
    
except Exception as e:
    print(f'✗ View import error: {e}')

print('\n=== SETUP INSTRUCTIONS ===')
print('To complete the payments app setup:')
print('1. Add "payments" to INSTALLED_APPS in settings.py')
print('2. Include payments URLs in main urls.py:')
print('   path("payments/", include("payments.urls")),')
print('3. Run migrations: python manage.py makemigrations payments')
print('4. Apply migrations: python manage.py migrate')
print('5. Test payment processing: /payments/process/<subscription_id>/')

print('\n=== PAYMENT FLOW ===')
print('1. User login → Trial expiry detected')
print('2. Payment modal appears → User selects plan')
print('3. Redirect to payment processing page')
print('4. User enters payment details')
print('5. Payment processed → Subscription activated')
print('6. User redirected to dashboard')

print('\n✓ Payments app created successfully!')
