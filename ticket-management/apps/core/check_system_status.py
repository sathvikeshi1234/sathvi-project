#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from superadmin.models import Company, Subscription
from django.utils import timezone

print('=== Check Current System Status ===')

try:
    # Check admin user
    admin_user = User.objects.get(username='TestSathvika')
    print(f'Admin User: {admin_user.username}')
    print(f'Email: {admin_user.email}')
    print(f'Is Staff: {admin_user.is_staff}')
    
    # Check company
    company = Company.objects.get(name='TestSathvika Company')
    print(f'\nCompany: {company.name}')
    print(f'Subscription Status: {company.subscription_status}')
    
    # Check subscription
    subscription = Subscription.objects.get(company=company)
    print(f'\nSubscription Details:')
    print(f'Plan: {subscription.plan.name}')
    print(f'Status: {subscription.status}')
    print(f'Start Date: {subscription.start_date}')
    print(f'End Date: {subscription.end_date}')
    print(f'Today: {timezone.now().date()}')
    
    # Check expiry status
    days_remaining = (subscription.end_date - timezone.now().date()).days
    print(f'Days Remaining: {days_remaining}')
    print(f'Trial Active: {subscription.is_trial_active}')
    print(f'Payment Required: {subscription.is_payment_required}')
    print(f'Can Access Dashboard: {subscription.can_access_dashboard(admin_user)}')
    
    # Test helper functions
    from superadmin.views import check_subscription_expiry
    should_show_modal = check_subscription_expiry(admin_user)
    print(f'\nModal Check:')
    print(f'Should Show Modal: {should_show_modal}')
    
    if should_show_modal:
        print('✅ READY: Modal will appear on login')
    else:
        print('❌ NOT READY: Modal will not appear')
        
    print(f'\n=== Test Commands ===')
    print('Force expired trial: python force_expired_trial.py')
    print('Restore trial: python restore_trial.py')
    print('Test login: http://127.0.0.1:8000/superadmin/login/')
    
except Exception as e:
    print(f'Error: {e}')
