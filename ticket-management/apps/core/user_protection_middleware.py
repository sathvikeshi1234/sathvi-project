"""
User Protection Middleware to prevent accidental deactivation
"""

from django.contrib.auth.models import User
from users.models import UserProfile


class UserProtectionMiddleware:
    """
    Middleware to protect critical users from accidental deactivation
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Only check for authenticated users
        if request.user.is_authenticated:
            # Critical users that should never be deactivated
            critical_users = [
                'pandu', 'testlogin', 'testuser', 'midhun', 
                'monika', 'sai1', 'customer1', 'customer2', 
                'customer3', 'ramesh', 'vasu', 'yash'
            ]
            
            # If this is a critical user, ensure they stay active
            if request.user.username in critical_users:
                user_needs_reactivation = False
                profile_needs_reactivation = False
                
                # Check user status
                if not request.user.is_active:
                    request.user.is_active = True
                    request.user.save()
                    user_needs_reactivation = True
                
                # Check profile status
                try:
                    profile = request.user.userprofile
                    if not profile.is_active:
                        profile.is_active = True
                        profile.save()
                        profile_needs_reactivation = True
                except UserProfile.DoesNotExist:
                    # Create profile if missing
                    from users.models import Role
                    user_role, _ = Role.objects.get_or_create(name='User')
                    UserProfile.objects.create(
                        user=request.user,
                        role=user_role,
                        is_active=True
                    )
                    profile_needs_reactivation = True
                
                # Log if reactivation happened
                if user_needs_reactivation or profile_needs_reactivation:
                    print(f"USER PROTECTION: Reactivated {request.user.username}")
        
        response = self.get_response(request)
        return response
