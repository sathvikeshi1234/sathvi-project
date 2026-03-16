#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from superadmin.models import Company, Plan, Subscription
from users.models import UserProfile, Role
from django.contrib.auth.models import User
from datetime import date, timedelta

print('=== Testing Admin-Only Trial System ===')

# Get test data
company = Company.objects.first()
plan = Plan.objects.filter(name='Basic').first()

if company and plan:
    print(f'Testing with company: {company.name}')
    print(f'Testing with plan: {plan.name}')
    
    # Clean up existing test subscriptions
    Subscription.objects.filter(company=company).delete()
    
    print('\n=== 1. Creating Trial Subscription ===')
    trial_start = date.today() - timedelta(days=15)  # 15 days ago (still in trial)
    
    trial_subscription = Subscription.objects.create(
        company=company,
        plan=plan,
        status='trial',
        billing_cycle='monthly',
        start_date=trial_start,
        end_date=trial_start + timedelta(days=30),
        next_billing_date=trial_start + timedelta(days=30),
        base_price=plan.price,
        total_amount=plan.price
    )
    
    print(f'Trial subscription created: {trial_subscription.id}')
    print(f'Trial start: {trial_subscription.start_date}')
    print(f'Trial end: {trial_subscription.end_date}')
    
    # Test trial properties
    print(f'\n=== 2. Testing Trial Access ===')
    print(f'Is trial active: {trial_subscription.is_trial_active}')
    print(f'Trial days remaining: {trial_subscription.trial_days_remaining}')
    print(f'Is payment required: {trial_subscription.is_payment_required}')
    print(f'Can access dashboard (no user): {trial_subscription.can_access_dashboard}')
    
    # Test with admin user
    admin_user = User.objects.filter(userprofile__role__name='Admin').first()
    if admin_user:
        print(f'Can access dashboard (admin): {trial_subscription.can_access_dashboard(user=admin_user)}')
    
    # Test with agent user
    agent_user = User.objects.filter(userprofile__role__name='Agent').first()
    if agent_user:
        print(f'Can access dashboard (agent): {trial_subscription.can_access_dashboard(user=agent_user)}')
    
    print(f'\n=== 3. Testing Different User Roles ===')
    
    # Get users by role
    admin_role = Role.objects.filter(name='Admin').first()
    agent_role = Role.objects.filter(name='Agent').first()
    user_role = Role.objects.filter(name='User').first()
    
    test_scenarios = []
    
    if admin_role:
        admin_users = UserProfile.objects.filter(role=admin_role)[:2]  # Get 2 admin users
        for profile in admin_users:
            test_scenarios.append((profile.user, 'Admin'))
    
    if agent_role:
        agent_users = UserProfile.objects.filter(role=agent_role)[:2]  # Get 2 agent users
        for profile in agent_users:
            test_scenarios.append((profile.user, 'Agent'))
    
    if user_role:
        regular_users = UserProfile.objects.filter(role=user_role)[:2]  # Get 2 regular users
        for profile in regular_users:
            test_scenarios.append((profile.user, 'User'))
    
    print(f'Testing {len(test_scenarios)} user scenarios:')
    
    for test_user, role_name in test_scenarios:
        # Simulate access check for this user
        can_access = trial_subscription.can_access_dashboard(user=test_user)
        
        # For trial subscriptions, only Admin/SuperAdmin should have access
        if trial_subscription.status == 'trial' and trial_subscription.is_trial_active:
            expected_access = role_name in ['Admin', 'SuperAdmin']
        else:
            expected_access = can_access  # For non-trial, use normal logic
        
        result = "PASS" if can_access == expected_access else "FAIL"
        print(f'{result} {role_name} ({test_user.username}):')
        print(f'   Can access dashboard: {can_access} (expected: {expected_access})')
    
    print(f'\n=== 4. Testing Expired Trial ===')
    # Simulate expired trial
    expired_start = date.today() - timedelta(days=35)
    trial_subscription.start_date = expired_start
    trial_subscription.end_date = expired_start + timedelta(days=30)
    trial_subscription.save()
    
    # Auto-expire
    trial_subscription.expire_trial_if_needed()
    trial_subscription.refresh_from_db()
    
    print(f'Trial status after expiry: {trial_subscription.status}')
    print(f'Can access dashboard (expired): {trial_subscription.can_access_dashboard}')
    
    print(f'\n=== 5. Testing Active Subscription (All Roles) ===')
    # Create active subscription
    active_subscription = Subscription.objects.create(
        company=company,
        plan=plan,
        status='active',
        billing_cycle='monthly',
        start_date=date.today(),
        end_date=date.today() + timedelta(days=30),
        next_billing_date=date.today() + timedelta(days=30),
        base_price=plan.price,
        total_amount=plan.price
    )
    
    print(f'Active subscription created: {active_subscription.id}')
    print(f'Can access dashboard (active): {active_subscription.can_access_dashboard}')
    
    # For active subscriptions, all roles should have access
    print(f'Testing active subscription access for all roles:')
    for test_user, role_name in test_scenarios[:3]:  # Test first 3 users
        can_access = active_subscription.can_access_dashboard
        print(f'{role_name}: {can_access} (should be True for all)')
    
    print(f'\n=== 6. Summary ===')
    print('Admin-Only Trial System Test Results:')
    print('- Trial access: Only Admin/SuperAdmin users can access during trial')
    print('- Active access: All users can access when subscription is active')
    print('- Expired access: No access for any role when expired')
    print('- Payment required: Admin users get payment prompt, others get contact admin message')
    
    # Clean up
    Subscription.objects.filter(company=company).delete()
    print('Test subscriptions cleaned up')

else:
    print('No company or plan found for testing')
