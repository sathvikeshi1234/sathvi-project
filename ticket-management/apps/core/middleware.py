"""
Payment Middleware for checking user subscription status
"""

from django.shortcuts import redirect
from django.urls import reverse
from django.http import JsonResponse
from django.conf import settings
from .models import Subscription


class PaymentMiddleware:
    """
    Middleware to check if user has paid subscription
    Redirects unpaid users to payment modal
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Skip middleware for certain paths
        if self.should_skip_middleware(request):
            response = self.get_response(request)
            return response
        
        # Check if user is authenticated
        if request.user.is_authenticated:
            # Get or create subscription for user
            subscription, created = Subscription.objects.get_or_create(
                user=request.user,
                defaults={'status': 'unpaid'}
            )
            
            # Add subscription info to request
            request.subscription = subscription
            request.needs_payment = subscription.needs_payment()
            request.is_paid_user = subscription.is_paid()
            
            # Handle API requests differently
            if request.path.startswith('/api/'):
                if request.needs_payment:
                    return JsonResponse({
                        'error': 'Payment required',
                        'needs_payment': True,
                        'redirect_url': reverse('payment_modal')
                    }, status=402)
            
            # For web requests, add payment status to template context
            else:
                # Check if user needs payment and is not already on payment page
                if request.needs_payment and request.path != reverse('payment_modal'):
                    # Store intended URL for redirect after payment
                    request.session['intended_url'] = request.get_full_path()
                    
                    # For AJAX requests, return JSON response
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'needs_payment': True,
                            'redirect_url': reverse('payment_modal'),
                            'message': 'Payment required to access this feature'
                        })
        
        response = self.get_response(request)
        return response
    
    def should_skip_middleware(self, request):
        """Skip middleware for certain paths"""
        skip_paths = [
            '/admin/',
            '/login/',
            '/logout/',
            '/register/',
            '/static/',
            '/media/',
            reverse('payment_modal') if hasattr(reverse, '__call__') else '/payment/',
        ]
        
        # Check if path starts with any skip path
        for skip_path in skip_paths:
            if request.path.startswith(skip_path):
                return True
        
        # Skip for health checks and API docs
        if request.path in ['/health/', '/api/health/', '/docs/']:
            return True
        
        return False


def subscription_context_processor(request):
    """
    Add subscription information to template context
    """
    context = {}
    
    if request.user.is_authenticated:
        try:
            subscription = getattr(request, 'subscription', None)
            if not subscription:
                subscription = Subscription.objects.filter(user=request.user).first()
            
            if subscription:
                context.update({
                    'subscription': subscription,
                    'needs_payment': subscription.needs_payment(),
                    'is_paid_user': subscription.is_paid(),
                    'is_trial_active': subscription.is_trial_active(),
                    'trial_days_remaining': subscription.get_trial_days_remaining(),
                    'plan': subscription.plan,
                })
            else:
                context.update({
                    'subscription': None,
                    'needs_payment': True,
                    'is_paid_user': False,
                    'is_trial_active': False,
                    'trial_days_remaining': 0,
                    'plan': None,
                })
        except Exception:
            # Fallback values in case of any error
            context.update({
                'subscription': None,
                'needs_payment': True,
                'is_paid_user': False,
                'is_trial_active': False,
                'trial_days_remaining': 0,
                'plan': None,
            })
    
    return context
