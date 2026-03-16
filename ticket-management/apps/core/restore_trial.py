#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from superadmin.models import Company, Subscription
from django.utils import timezone

print('=== Restore Trial ===')

try:
    # Find the admin user
    admin_user = User.objects.get(username='TestSathvika')
    print(f'Found admin user: {admin_user.username}')
    
    # Find the admin's subscription
    company = Company.objects.get(name='TestSathvika Company')
    subscription = Subscription.objects.get(company=company)
    
    # Restore the trial by setting end date to 30 days from now
    future_date = timezone.now().date() + timezone.timedelta(days=30)
    subscription.end_date = future_date
    subscription.save()
    
    print(f'Trial restored - New end date: {subscription.end_date}')
    print(f'Today: {timezone.now().date()}')
    print(f'Days remaining: {(subscription.end_date - timezone.now().date()).days}')
    
    # Test helper functions
    from superadmin.views import check_subscription_expiry
    
    is_expired = check_subscription_expiry(admin_user)
    print(f'Should show modal: {is_expired}')
    
    if not is_expired:
        print('SUCCESS: Modal will NOT show - trial is active')
    else:
        print('ISSUE: Modal will still show')
    
except Exception as e:
    print(f'Error: {e}')
