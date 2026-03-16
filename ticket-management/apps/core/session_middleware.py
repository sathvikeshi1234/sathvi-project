"""
Session Management Middleware to prevent multiple concurrent logins
"""
from django.conf import settings
from django.contrib.auth import logout
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.urls import reverse

class SingleSessionMiddleware:
    """
    Middleware to ensure each user can only have one active session at a time.
    When a user logs in, all other sessions for that user are invalidated.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Only process for authenticated users (after auth middleware)
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Get current session key
            current_session_key = request.session.session_key
            
            if current_session_key:
                # Find all other sessions for this user
                other_sessions = Session.objects.filter(
                    session_data__contains=f'"user_id":{request.user.id}'
                ).exclude(session_key=current_session_key)
                
                # Delete other sessions (this effectively logs out from other tabs/browsers)
                other_sessions.delete()
        
        response = self.get_response(request)
        return response


class DashboardRedirectMiddleware:
    """
    Middleware to ensure users are always redirected to their correct dashboard
    based on their role, preventing cross-role dashboard access
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Only process for authenticated users accessing dashboard URLs
        if (hasattr(request, 'user') and 
            request.user.is_authenticated and 
            '/dashboard/' in request.path and 
            request.method == 'GET'):
            
            # Get user's role using the same validation functions
            try:
                from dashboards.views import is_admin_user, is_agent_user, is_regular_user
                
                # Define expected dashboard paths for each role
                if is_admin_user(request):
                    expected_dashboard = '/dashboard/admin-dashboard/'
                elif is_agent_user(request):
                    expected_dashboard = '/dashboard/agent-dashboard/'
                elif is_regular_user(request):
                    expected_dashboard = '/dashboard/user-dashboard/'
                else:
                    expected_dashboard = None
                
                # If user has a valid role and is accessing wrong dashboard
                if expected_dashboard and expected_dashboard not in request.path:
                    # Check if they're trying to access a different role's dashboard
                    wrong_dashboards = ['/dashboard/admin-dashboard/', '/dashboard/agent-dashboard/', '/dashboard/user-dashboard/']
                    for wrong_dashboard in wrong_dashboards:
                        if wrong_dashboard in request.path and wrong_dashboard != expected_dashboard:
                            # Redirect to correct dashboard
                            return HttpResponseRedirect(expected_dashboard)
                            
            except ImportError:
                # If imports fail, skip the check
                pass
        
        response = self.get_response(request)
        return response
