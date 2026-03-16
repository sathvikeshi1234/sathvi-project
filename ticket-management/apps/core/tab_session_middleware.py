"""
Tab-Specific Session Management to prevent cross-tab session interference
"""
from django.contrib.auth import login, logout
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.urls import reverse
import hashlib
import json

class TabSessionMiddleware:
    """
    Middleware to create tab-specific sessions to prevent cross-tab interference
    """
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Generate a unique tab identifier if not present
        if 'tab_id' not in request.session:
            # Create unique tab ID based on user agent and timestamp
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            timestamp = str(timezone.now().timestamp())
            tab_id = hashlib.md5(f"{user_agent}{timestamp}".encode()).hexdigest()[:16]
            request.session['tab_id'] = tab_id
            request.session.modified = True
        
        # Only process for authenticated users
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Store current user info in tab-specific session
            current_user_id = request.user.id
            current_user_role = self.get_user_role(request.user)
            
            # Check if this tab session contains different user data
            session_user_id = request.session.get('tab_user_id')
            session_user_role = request.session.get('tab_user_role')
            
            # If session has different user, clear it and set current user
            if session_user_id and session_user_id != current_user_id:
                # Clear session data for previous user
                self.clear_tab_session_data(request)
                
                # Set current user data
                request.session['tab_user_id'] = current_user_id
                request.session['tab_user_role'] = current_user_role
                request.session.modified = True
            elif not session_user_id:
                # First time user in this tab
                request.session['tab_user_id'] = current_user_id
                request.session['tab_user_role'] = current_user_role
                request.session.modified = True
        
        response = self.get_response(request)
        return response
    
    def clear_tab_session_data(self, request):
        """Clear user-specific session data but keep tab_id"""
        tab_id = request.session.get('tab_id')
        request.session.flush()
        if tab_id:
            request.session['tab_id'] = tab_id
        request.session.modified = True
    
    def get_user_role(self, user):
        """Get user's role name"""
        try:
            if hasattr(user, 'userprofile') and getattr(user.userprofile, 'role', None):
                return getattr(user.userprofile.role, 'name', '').lower()
        except:
            pass
        return 'unknown'


class StrictDashboardMiddleware:
    """
    Strict middleware that enforces dashboard access based on current session user
    """
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Only process for dashboard URLs
        if (hasattr(request, 'user') and 
            request.user.is_authenticated and 
            '/dashboard/' in request.path and 
            request.method == 'GET'):
            
            # Get current user role
            current_role = self.get_user_role(request.user)
            
            # Get session role (should match current role)
            session_role = request.session.get('tab_user_role')
            
            # If roles don't match, there's a session conflict
            if session_role and session_role != current_role:
                # Force logout and redirect to login
                logout(request)
                return HttpResponseRedirect(reverse('users:login'))
            
            # Define dashboard mappings
            dashboard_map = {
                'admin': '/dashboard/admin-dashboard/',
                'agent': '/dashboard/agent-dashboard/',
                'user': '/dashboard/user-dashboard/',
                'customer': '/dashboard/user-dashboard/',
            }
            
            # Get expected dashboard for current role
            expected_dashboard = dashboard_map.get(current_role)
            
            # If user is accessing wrong dashboard, redirect to correct one
            if expected_dashboard and not request.path.startswith(expected_dashboard):
                return HttpResponseRedirect(expected_dashboard)
        
        response = self.get_response(request)
        return response
    
    def get_user_role(self, user):
        """Get user's role name"""
        try:
            if hasattr(user, 'userprofile') and getattr(user.userprofile, 'role', None):
                return getattr(user.userprofile.role, 'name', '').lower()
        except:
            pass
        return 'unknown'


class LoginSessionMiddleware:
    """
    Middleware to handle login-specific session management
    """
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Process login requests
        if request.path in ['/login/', '/users/login/'] and request.method == 'POST':
            # Clear any existing tab session data before new login
            if 'tab_id' in request.session:
                tab_id = request.session['tab_id']
                request.session.flush()
                request.session['tab_id'] = tab_id
                request.session.modified = True
        
        response = self.get_response(request)
        return response
