"""
Middleware to enforce system settings like maintenance mode, user registration, etc.
"""

from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponse
from .models import SiteSettings


class SystemSettingsMiddleware:
    """
    Middleware to enforce system-wide settings
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            # Get system settings
            settings = SiteSettings.get_solo()
            
            # 1. MAINTENANCE MODE
            if settings.maintenance_mode:
                # Allow admin users to access during maintenance
                if request.user.is_authenticated and (
                    request.user.is_superuser or 
                    request.user.is_staff or
                    (hasattr(request.user, 'userprofile') and 
                     getattr(request.user.userprofile.role, 'name', '').lower() == 'admin')
                ):
                    pass  # Admin can access during maintenance
                else:
                    # Show maintenance page for non-admin users
                    if request.path not in ['/maintenance/', '/login/', '/logout/']:
                        return HttpResponse('''
                            <div style="display: flex; justify-content: center; align-items: center; height: 100vh; font-family: Arial, sans-serif;">
                                <div style="text-align: center; padding: 40px; border: 1px solid #ddd; border-radius: 8px;">
                                    <h2>🔧 Under Maintenance</h2>
                                    <p>We're currently performing scheduled maintenance.</p>
                                    <p>Please try again later. Thank you for your patience!</p>
                                    <small>Admin users can still access the system.</small>
                                </div>
                            </div>
                        ''', status=503)
            
            # 2. USER REGISTRATION CONTROL
            # This is handled in the registration views, but we can add middleware logic here if needed
            
            # 3. EMAIL VERIFICATION REQUIREMENT
            # This would be checked in login/registration views
            
            # 4. REMEMBER ME FUNCTIONALITY
            # This affects login session duration
            
            # 5. TUTORIAL DISPLAY
            # Add tutorial flag to session if needed
            if settings.show_tutorial and request.user.is_authenticated:
                if 'tutorial_shown' not in request.session:
                    request.session['should_show_tutorial'] = True
            
        except Exception as e:
            # If settings can't be loaded, continue without enforcing them
            print(f"Error loading system settings: {e}")
        
        response = self.get_response(request)
        return response


class UserRegistrationMiddleware:
    """
    Middleware to control user registration based on system settings
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            settings = SiteSettings.get_solo()
            
            # Block registration URLs if user registration is disabled
            if not settings.user_registration:
                registration_urls = ['/users/register/', '/register/', '/signup/']
                if any(request.path.startswith(url) for url in registration_urls):
                    messages.error(request, "User registration is currently disabled.")
                    return redirect('users:login')
        
        except Exception as e:
            print(f"Error checking user registration setting: {e}")
        
        response = self.get_response(request)
        return response
