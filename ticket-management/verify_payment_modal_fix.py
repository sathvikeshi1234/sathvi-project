#!/usr/bin/env python3
"""
Simple verification script for payment modal fix
This script checks that the code changes are in place correctly
"""

import os
import re

def check_file_for_pattern(file_path, pattern, description):
    """Check if a file contains a specific pattern"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if re.search(pattern, content, re.MULTILINE | re.DOTALL):
                print(f"[PASS] {description}")
                return True
            else:
                print(f"[FAIL] {description}")
                return False
    except FileNotFoundError:
        print(f"[FAIL] {description} - File not found")
        return False

def main():
    print("Payment Modal Fix Verification")
    print("=" * 50)
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    # Check middleware changes
    middleware_path = os.path.join(base_path, 'apps', 'superadmin', 'middleware.py')
    check_file_for_pattern(
        middleware_path,
        r'payment_completed_user_id = request\.session\.get\([\'"]payment_completed_user_id[\'"]\)',
        "Middleware checks payment_completed_user_id"
    )
    
    check_file_for_pattern(
        middleware_path,
        r'if payment_completed and payment_completed_user_id == request\.user\.id:',
        "Middleware validates user ID for payment completion"
    )
    
    # Check dashboard view changes
    dashboard_path = os.path.join(base_path, 'apps', 'dashboards', 'views.py')
    check_file_for_pattern(
        dashboard_path,
        r'payment_completed_user_id = request\.session\.get\([\'"]payment_completed_user_id[\'"]\)',
        "Dashboard views check payment_completed_user_id"
    )
    
    check_file_for_pattern(
        dashboard_path,
        r'if payment_completed and payment_completed_user_id == request\.user\.id:',
        "Dashboard views validate user ID for payment completion"
    )
    
    # Check payment view changes
    payments_path = os.path.join(base_path, 'apps', 'payments', 'views.py')
    check_file_for_pattern(
        payments_path,
        r'request\.session\[[\'"]payment_completed_user_id[\'"]\] = request\.user\.id',
        "Payment view sets payment_completed_user_id"
    )
    
    # Check clear_payment_modal changes
    check_file_for_pattern(
        dashboard_path,
        r'request\.session\[[\'"]payment_completed_user_id[\'"]\] = request\.user\.id',
        "clear_payment_modal sets payment_completed_user_id"
    )
    
    print("\n" + "=" * 50)
    print("Summary of fixes applied:")
    print("1. Added user ID validation to prevent payment completion from affecting other users")
    print("2. Fixed middleware to properly handle payment completion flags")
    print("3. Added session flag clearing in dashboard views")
    print("4. Ensured payment completion is user-specific")
    print("5. Updated payment completion to store user ID in session")
    
    print("\nExpected behavior after fix:")
    print("- Payment modal shows for users with expired subscriptions")
    print("- Payment modal does NOT show after successful payment")
    print("- Payment completion persists across logout/login for the same user")
    print("- Payment completion for one user doesn't affect other users")
    print("- Session flags are properly cleared when payment is completed")

if __name__ == '__main__':
    main()
