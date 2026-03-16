#!/usr/bin/env python3
"""
Simple verification script for settings page
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
    print("Settings Page Fix Verification")
    print("=" * 50)
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    # Check URL routing
    urls_path = os.path.join(base_path, 'apps', 'dashboards', 'urls.py')
    check_file_for_pattern(
        urls_path,
        r"path\('user-dashboard/<str:page>/'",
        "URL routing for user-dashboard pages exists"
    )
    
    # Check view function
    views_path = os.path.join(base_path, 'apps', 'dashboards', 'views.py')
    check_file_for_pattern(
        views_path,
        r"def user_dashboard_page\(request, page: str\):",
        "user_dashboard_page view function exists"
    )
    
    check_file_for_pattern(
        views_path,
        r"if template_file == 'settings.html':",
        "Settings page handling in view exists"
    )
    
    check_file_for_pattern(
        views_path,
        r"'settings': 'settings.html'",
        "Settings page mapping exists"
    )
    
    check_file_for_pattern(
        views_path,
        r"UserProfile\.objects\.get_or_create\(user=request\.user\)",
        "UserProfile handling exists"
    )
    
    check_file_for_pattern(
        views_path,
        r"settings_dark_mode.*user_profile\.dark_mode",
        "Settings context variables exist"
    )
    
    # Check template exists
    template_path = os.path.join(base_path, 'templates', 'userdashboard', 'settings.html')
    check_file_for_pattern(
        template_path,
        r"<title>TicketHub - Ticket Management System</title>",
        "Settings template exists"
    )
    
    # Check CSS exists
    css_path = os.path.join(base_path, 'static', 'userdashboard', 'css', 'settings.css')
    check_file_for_pattern(
        css_path,
        r".*",
        "Settings CSS exists"
    )
    
    print("\n" + "=" * 50)
    print("Summary of fixes applied:")
    print("1. Added settings page handling to user_dashboard_page view")
    print("2. Added UserProfile integration for user preferences")
    print("3. Added POST request handling for settings updates")
    print("4. Added context variables for template rendering")
    print("5. Added password change functionality")
    print("6. Added placeholder for 2FA and account management")
    
    print("\nExpected behavior:")
    print("- Settings page should load at /dashboard/user-dashboard/settings/")
    print("- User preferences should be saved to UserProfile")
    print("- Form submissions should update user settings")
    print("- Messages should show success/error feedback")

if __name__ == '__main__':
    main()
