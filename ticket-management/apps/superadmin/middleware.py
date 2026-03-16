"""
Middleware to check user subscription expiry and show payment modal
"""

from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from superadmin.models import Subscription, Company


class SubscriptionExpiryMiddleware:
    """
    Middleware to check if user's subscription has expired
    and redirect to payment modal if needed
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only check for authenticated users
        if request.user.is_authenticated:
            
            # IMPORTANT: If payment was completed, don't do anything else
            payment_completed = request.session.get('payment_completed', False)
            payment_completed_user_id = request.session.get('payment_completed_user_id')
            
            if payment_completed and payment_completed_user_id == request.user.id:
                # Just ensure modal flags are cleared and keep payment_completed flag
                if 'show_payment_modal' in request.session:
                    del request.session['show_payment_modal']
                if 'expiry_info' in request.session:
                    del request.session['expiry_info']
                # Keep payment_completed flag set to prevent future modal shows
                request.session.modified = True
            else:
                # Check if user needs to see payment modal
                if self.should_show_payment_modal(request):
                    # Set session flag to show modal
                    request.session['show_payment_modal'] = True
                    request.session['expiry_info'] = {
                        'plan_name': self.get_user_plan_name(request),
                        'expiry_date': self.get_expiry_date(request),
                        'days_expired': self.get_days_expired(request),
                    }
                else:
                    # Clear session flags if subscription is active or payment was completed
                    if 'show_payment_modal' in request.session:
                        del request.session['show_payment_modal']
                    if 'expiry_info' in request.session:
                        del request.session['expiry_info']
                    request.session.modified = True
        
        response = self.get_response(request)
        return response
    
    def should_show_payment_modal(self, request):
        """Check if user should see payment modal"""
        try:
            # Skip for certain URLs (login, logout, payment pages)
            skip_urls = [
                reverse('superadmin:superadmin_login'),
                reverse('superadmin:superadmin_logout'),
                '/superadmin/payments/',
                '/superadmin/subscriptions/payment/',
            ]
            
            if request.path in skip_urls:
                return False
            
            # IMPORTANT: Check payment_completed flag FIRST
            if request.session.get('payment_completed', False):
                return False
            
            # Use the same logic as the should_show_payment_modal function in views.py
            from superadmin.views import should_show_payment_modal
            return should_show_payment_modal(request.user)
            
        except Exception as e:
            print(f"Error in subscription check: {e}")
            return False
    
    def get_user_subscription(self, request):
        """Get user's subscription"""
        try:
            # Find user's company and subscription
            from users.models import UserProfile
            
            profile = getattr(request.user, 'userprofile', None)
            
            # Try multiple company naming patterns
            company_patterns = [
                f'{request.user.username} Company',  # username pattern
                f"{request.user.get_full_name()}'s Company",  # full name pattern
                f"{request.user.first_name} {request.user.last_name}'s Company",  # explicit name pattern
            ]
            
            # Check for company with known naming patterns first
            for pattern in company_patterns:
                company = Company.objects.filter(name=pattern).first()
                if company:
                    subscription = company.subscriptions.order_by('-created_at').first()
                    if subscription:
                        return subscription
            
            # Fallback: Check if user profile has company association
            if profile:
                companies = Company.objects.all()
                for company in companies:
                    if hasattr(company, 'users') and request.user in company.users.all():
                        return company.subscriptions.order_by('-created_at').first()
            
            return None
            
        except Exception as e:
            print(f"Error getting user subscription: {e}")
            return None

    
    def get_user_plan_name(self, request):
        """Get user's current plan name"""
        try:
            subscription = self.get_user_subscription(request)
            if subscription and subscription.plan:
                return subscription.plan.name
            return "Trial"
        except:
            return "Trial"
    
    def get_expiry_date(self, request):
        """Get subscription expiry date"""
        try:
            subscription = self.get_user_subscription(request)
            if subscription:
                return subscription.end_date.strftime('%B %d, %Y')
            return None
        except:
            return None
    
    def get_days_expired(self, request):
        """Get days since expiry"""
        try:
            subscription = self.get_user_subscription(request)
            if subscription:
                today = timezone.now().date()
                if subscription.end_date < today:
                    return (today - subscription.end_date).days
            return 0
        except:
            return 0
