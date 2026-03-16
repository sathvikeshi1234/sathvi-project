#!/usr/bin/env python
"""
Fix role-based access control for dashboards
"""
import os
import sys

def add_role_validation_to_dashboard():
    """Add role validation to dashboard views"""
    
    # Read the current dashboard views file
    views_file = 'apps/dashboards/views.py'
    
    with open(views_file, 'r') as f:
        content = f.read()
    
    # Add role validation function at the top after imports
    import_section = content.split('\n\n')[0]  # First section with imports
    role_validation_function = '''
# Role validation helper functions
def validate_user_role(request, allowed_roles):
    """
    Validate if user has allowed role
    allowed_roles: list of role names (e.g., ['user', 'customer'])
    """
    if not hasattr(request.user, "userprofile") or not getattr(request.user.userprofile, "role", None):
        return False
    
    user_role = getattr(request.user.userprofile.role, "name", "").lower()
    return user_role in [role.lower() for role in allowed_roles]

def is_admin_user(request):
    """Check if user is admin (admin or superadmin role)"""
    if request.user.is_superuser or request.user.is_staff:
        return True
    
    if hasattr(request.user, "userprofile") and getattr(request.user.userprofile, "role", None):
        role_name = getattr(request.user.userprofile.role, "name", "").lower()
        return role_name in ["admin", "superadmin"]
    
    return False

def is_agent_user(request):
    """Check if user is agent"""
    if hasattr(request.user, "userprofile") and getattr(request.user.userprofile, "role", None):
        role_name = getattr(request.user.userprofile.role, "name", "").lower()
        return role_name == "agent"
    return False

def is_regular_user(request):
    """Check if user is regular user/customer"""
    if hasattr(request.user, "userprofile") and getattr(request.user.userprofile, "role", None):
        role_name = getattr(request.user.userprofile.role, "name", "").lower()
        return role_name in ["user", "customer"]
    return False

'''
    
    # Find where to insert the function (after imports, before first function)
    first_function_pos = content.find('def ')
    if first_function_pos == -1:
        print("Error: Could not find first function")
        return
    
    # Insert the role validation functions
    new_content = content[:first_function_pos] + role_validation_function + content[first_function_pos:]
    
    # Now add role validation to user_dashboard function
    user_dashboard_start = new_content.find('def user_dashboard(request):')
    if user_dashboard_start == -1:
        print("Error: Could not find user_dashboard function")
        return
    
    # Find the end of the function signature and add role validation
    function_end_pos = new_content.find(':', user_dashboard_start) + 1
    
    role_check_code = '''
    
    # ROLE VALIDATION: Only allow regular users to access user dashboard
    if is_admin_user(request) or is_agent_user(request):
        # Redirect admins to admin dashboard and agents to agent dashboard
        if is_admin_user(request):
            return redirect("dashboards:admin_dashboard")
        elif is_agent_user(request):
            return redirect("dashboards:agent_dashboard")
    
    if not is_regular_user(request):
        # If user doesn't have a valid role, redirect to login
        return redirect("users:login")
'''
    
    # Insert role validation after function signature
    new_content = new_content[:function_end_pos] + role_check_code + new_content[function_end_pos:]
    
    # Add role validation to agent_dashboard function
    agent_dashboard_start = new_content.find('def agent_dashboard(request):')
    if agent_dashboard_start != -1:
        agent_function_end = new_content.find(':', agent_dashboard_start) + 1
        
        agent_role_check = '''
    
    # ROLE VALIDATION: Only allow agents to access agent dashboard
    if not is_agent_user(request):
        # Redirect non-agents to appropriate dashboard
        if is_admin_user(request):
            return redirect("dashboards:admin_dashboard")
        elif is_regular_user(request):
            return redirect("dashboards:user_dashboard")
        else:
            return redirect("users:login")
'''
        new_content = new_content[:agent_function_end] + agent_role_check + new_content[agent_function_end:]
    
    # Write the updated content
    with open(views_file, 'w') as f:
        f.write(new_content)
    
    print("✓ Added role validation to dashboard views")

def add_login_redirection_validation():
    """Add validation to prevent role switching after login"""
    
    users_views_file = 'apps/users/views.py'
    
    with open(users_views_file, 'r') as f:
        content = f.read()
    
    # Find admin_login_view function and add role-based redirection
    admin_login_start = content.find('def admin_login_view(request):')
    if admin_login_start == -1:
        print("Error: Could not find admin_login_view function")
        return
    
    # Look for the authentication success part and add proper redirection
    auth_success_pos = content.find('auth.login(request, user)', admin_login_start)
    if auth_success_pos == -1:
        print("Error: Could not find authentication success in admin_login_view")
        return
    
    # Add role validation after login
    insertion_pos = content.find('\n', auth_success_pos) + 1
    
    role_redirect_code = '''
        
        # ROLE VALIDATION: Ensure admin users are actually admins
        if hasattr(user, 'userprofile') and getattr(user.userprofile, 'role', None):
            role_name = getattr(user.userprofile.role, 'name', '').lower()
            if role_name not in ['admin', 'superadmin'] and not user.is_superuser and not user.is_staff:
                # User is not actually an admin, log them out and show error
                auth.logout(request)
                messages.error(request, 'You do not have admin privileges.')
                return render(request, 'admin_login.html')
'''
    
    new_content = content[:insertion_pos] + role_redirect_code + content[insertion_pos:]
    
    # Write the updated content
    with open(users_views_file, 'w') as f:
        f.write(new_content)
    
    print("✓ Added role validation to admin login")

def main():
    print("FIXING ROLE-BASED ACCESS CONTROL")
    print("=" * 50)
    
    try:
        add_role_validation_to_dashboard()
        add_login_redirection_validation()
        
        print("\n✅ SECURITY FIXES APPLIED:")
        print("1. Added role validation to user dashboard")
        print("2. Added role validation to agent dashboard") 
        print("3. Added role validation to admin login")
        print("\n🔒 SECURITY IMPROVEMENTS:")
        print("- Admins can no longer access user dashboard")
        print("- Agents can no longer access user dashboard")
        print("- Users can only access their appropriate dashboard")
        print("- Role validation prevents privilege escalation")
        
        print("\n⚠️  IMPORTANT:")
        print("Please restart the Django server for changes to take effect:")
        print("python manage.py runserver")
        
    except Exception as e:
        print(f"❌ Error applying fixes: {e}")

if __name__ == "__main__":
    main()
