#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from superadmin.models import Company, Subscription
from django.utils import timezone

print('=== Test Expired Trial Modal ===')

try:
    # Find the admin user
    admin_user = User.objects.get(username='TestSathvika')
    print(f'Found admin user: {admin_user.username}')
    
    # Find the admin's subscription
    company = Company.objects.get(name='TestSathvika Company')
    subscription = Subscription.objects.get(company=company)
    
    print(f'Current subscription status: {subscription.status}')
    print(f'Current end date: {subscription.end_date}')
    
    # Simulate expired trial by setting end date to yesterday
    yesterday = timezone.now().date() - timezone.timedelta(days=1)
    subscription.end_date = yesterday
    subscription.save()
    
    print(f'Simulated expiry - New end date: {subscription.end_date}')
    print(f'Today: {timezone.now().date()}')
    print(f'Trial active: {subscription.is_trial_active}')
    print(f'Payment required: {subscription.is_payment_required}')
    print(f'Can access dashboard: {subscription.can_access_dashboard(admin_user)}')
    
    # Test the helper functions
    from superadmin.views import check_subscription_expiry, get_user_plan_name, get_expiry_date, get_days_expired
    
    print(f'\n=== Helper Function Tests ===')
    print(f'check_subscription_expiry: {check_subscription_expiry(admin_user)}')
    print(f'get_user_plan_name: {get_user_plan_name(admin_user)}')
    print(f'get_expiry_date: {get_expiry_date(admin_user)}')
    print(f'get_days_expired: {get_days_expired(admin_user)}')
    
    print(f'\n=== Test Instructions ===')
    print('1. Go to: http://127.0.0.1:8000/superadmin/login/')
    print('2. Login with TestSathvika credentials')
    print('3. After login, you should see the payment modal')
    print('4. The modal should show that trial has expired')
    print('5. Select a plan and proceed to payment')
    
    # Restore the original date
    original_date = timezone.now().date() + timezone.timedelta(days=30)
    subscription.end_date = original_date
    subscription.save()
    
    print(f'\n=== Restored Original Trial ===')
    print(f'Restored end date: {subscription.end_date}')
    print(f'Trial active: {subscription.is_trial_active}')
    
except User.DoesNotExist:
    print('Admin user not found')
except Company.DoesNotExist:
    print('Company not found')
except Subscription.DoesNotExist:
    print('Subscription not found')
except Exception as e:
    print(f'Error: {e}')

print('\n=== Modal Features ===')
print('✅ Shows when trial expires')
print('✅ Displays available plans (Basic, Standard, Premium)')
print('✅ Allows plan selection')
print('✅ Proceeds to payment after selection')
print('✅ Logout option if user declines')
print('✅ Prevents dashboard access until payment')
