"""
Enhanced Session Management to prevent session overwriting between tabs
"""
from django.contrib.auth import login, logout
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.urls import reverse
import json

class SessionFixationMiddleware:
    """
    Middleware to prevent session fixation and ensure clean sessions
    """
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Process only for login requests
        if request.path in ['/login/', '/users/login/'] and request.method == 'POST':
            # Clear all existing sessions before allowing new login
            if hasattr(request, 'user') and request.user.is_authenticated:
                self.clear_all_user_sessions(request.user)
        
        response = self.get_response(request)
        return response
    
    def clear_all_user_sessions(self, user):
        """Clear all sessions for a specific user"""
        try:
            # Find all sessions for this user
            user_sessions = Session.objects.filter(
                session_data__contains=f'"user_id":{user.id}'
            )
            # Delete them all
            user_sessions.delete()
        except Exception as e:
            print(f"Error clearing user sessions: {e}")


class RoleSessionMiddleware:
    """
    Middleware to enforce role-based session separation
    """
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Only process for authenticated users
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Get current user role
            current_role = self.get_user_role(request.user)
            
            # Get session role
            session_role = request.session.get('user_role')
            
            # If no role in session, set it
            if not session_role:
                request.session['user_role'] = current_role
                request.session['user_id'] = request.user.id
                request.session.modified = True
            else:
                # If session role doesn't match current user role, something is wrong
                if session_role != current_role:
                    # Clear session and redirect to login
                    logout(request)
                    return HttpResponseRedirect(reverse('users:login'))
                
                # If session user_id doesn't match current user, session was hijacked
                if request.session.get('user_id') != request.user.id:
                    logout(request)
                    return HttpResponseRedirect(reverse('users:login'))
        
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


class DashboardAccessMiddleware:
    """
    Middleware to ensure users can only access their own dashboard
    """
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Only process for dashboard URLs
        if (hasattr(request, 'user') and 
            request.user.is_authenticated and 
            '/dashboard/' in request.path):
            
            # Get current user role
            user_role = self.get_user_role(request.user)
            
            # Define allowed dashboard paths for each role
            allowed_dashboards = {
                'admin': ['/dashboard/admin-dashboard/'],
                'agent': ['/dashboard/agent-dashboard/'],
                'user': ['/dashboard/user-dashboard/'],
                'customer': ['/dashboard/user-dashboard/'],
            }
            
            # Check if user is accessing allowed dashboard
            if user_role in allowed_dashboards:
                user_allowed_paths = allowed_dashboards[user_role]
                
                # Check if current path is allowed for this user
                path_allowed = False
                for allowed_path in user_allowed_paths:
                    if request.path.startswith(allowed_path):
                        path_allowed = True
                        break
                
                # If not allowed, redirect to correct dashboard
                if not path_allowed:
                    # Find the correct dashboard for this user
                    if user_role == 'admin':
                        return HttpResponseRedirect('/dashboard/admin-dashboard/')
                    elif user_role == 'agent':
                        return HttpResponseRedirect('/dashboard/agent-dashboard/')
                    elif user_role in ['user', 'customer']:
                        return HttpResponseRedirect('/dashboard/user-dashboard/')
        
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
