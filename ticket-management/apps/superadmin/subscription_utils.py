from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from superadmin.models import Subscription, Company
from users.models import UserProfile, Role

def subscription_required(view_func):
    """
    Decorator to check if user has active subscription or valid trial
    Admin/SuperAdmin users get trial access, others don't
    """
    def _wrapped_view(request, *args, **kwargs):
        # Get user's role
        try:
            user_profile = request.user.userprofile
            user_role = user_profile.role.name if user_profile.role else None
            
            # Get user's company (assuming there's a way to get this)
            # This might need adjustment based on your actual user-company relationship
            company = get_user_company(request.user)
            
            if not company:
                messages.error(request, 'No company associated with your account.')
                return redirect('subscription_required')
            
            # Get active subscription for this company
            subscription = Subscription.objects.filter(
                company=company,
                status__in=['active', 'trial']
            ).first()
            
            if not subscription:
                messages.error(request, 'No subscription found. Please contact support.')
                return redirect('subscription_required')
            
            # Check if user can access dashboard based on role and subscription
            if not subscription.can_access_dashboard:
                if subscription.is_payment_required:
                    if user_role in ['Admin', 'SuperAdmin']:
                        messages.error(request, 'Your trial has expired. Please make a payment to continue.')
                    else:
                        messages.error(request, 'Subscription expired. Please contact your admin.')
                    return redirect('payment_required')
                else:
                    messages.error(request, 'Your subscription is not active. Please contact support.')
                    return redirect('subscription_required')
            
            # Auto-expire trial if needed
            subscription.expire_trial_if_needed()
            
            return view_func(request, *args, **kwargs)
            
        except AttributeError:
            # User doesn't have proper profile setup
            messages.error(request, 'Account setup incomplete. Please contact support.')
            return redirect('subscription_required')
        except Exception as e:
            messages.error(request, 'Subscription check failed. Please try again.')
            return redirect('subscription_required')
    
    return _wrapped_view


def get_user_company(user):
    """
    Get the company associated with a user
    This is a placeholder - implement based on your actual user-company relationship
    """
    # This is a simplified implementation
    # In practice, you might have a UserProfile.company field or similar
    try:
        # Try to get company from user profile (if such field exists)
        profile = user.userprofile
        if hasattr(profile, 'company'):
            return profile.company
        
        # If no direct relationship, you might need to query through other means
        # For now, return the first company as a fallback
        return Company.objects.first()
    except:
        return None


def check_company_subscription(company):
    """
    Check if a company has valid subscription
    Returns tuple (can_access, subscription, reason)
    """
    subscription = Subscription.objects.filter(
        company=company,
        status__in=['active', 'trial']
    ).first()
    
    if not subscription:
        return False, None, 'No subscription found'
    
    # Auto-expire trial if needed
    subscription.expire_trial_if_needed()
    
    if subscription.can_access_dashboard:
        return True, subscription, 'Access granted'
    elif subscription.is_payment_required:
        return False, subscription, 'Payment required'
    else:
        return False, subscription, 'Subscription inactive'


def can_user_access_trial(user, subscription):
    """
    Check if a specific user can access trial based on their role
    """
    try:
        user_profile = user.userprofile
        user_role = user_profile.role.name if user_profile.role else None
        
        # Only Admin and SuperAdmin can access trials
        if subscription.status == 'trial' and subscription.is_trial_active:
            return user_role in ['Admin', 'SuperAdmin']
        
        return True  # Non-trial access is handled by subscription status
        
    except AttributeError:
        return False
