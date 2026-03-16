#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from superadmin.models import Company, Subscription
from django.utils import timezone

print('=== Force Expired Trial for Testing ===')

try:
    # Find the admin user
    admin_user = User.objects.get(username='TestSathvika')
    print(f'Found admin user: {admin_user.username}')
    
    # Find the admin's subscription
    company = Company.objects.get(name='TestSathvika Company')
    subscription = Subscription.objects.get(company=company)
    
    # Force expire the trial by setting end date to yesterday
    yesterday = timezone.now().date() - timezone.timedelta(days=1)
    subscription.end_date = yesterday
    subscription.save()
    
    print(f'Trial expired - End date: {subscription.end_date}')
    print(f'Today: {timezone.now().date()}')
    print(f'Days expired: {(timezone.now().date() - subscription.end_date).days}')
    
    # Test helper functions
    from superadmin.views import check_subscription_expiry
    
    is_expired = check_subscription_expiry(admin_user)
    print(f'Should show modal: {is_expired}')
    
    if is_expired:
        print('SUCCESS: Modal will show when user logs in')
    else:
        print('ISSUE: Modal will not show')
    
    print(f'\n=== Test Instructions ===')
    print('1. Go to: http://127.0.0.1:8000/superadmin/login/')
    print('2. Login with TestSathvika credentials')
    print('3. Payment modal should appear automatically')
    print('4. Select a plan to proceed to payment')
    
    print(f'\n=== To Restore Trial ===')
    print('Run: python restore_trial.py')
    
except Exception as e:
    print(f'Error: {e}')
