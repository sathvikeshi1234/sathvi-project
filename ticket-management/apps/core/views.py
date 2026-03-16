from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
from .models import Plan, Subscription, Payment
import json


@login_required
def dashboard(request):
    """
    Main dashboard view - only accessible to paid users
    """
    # Check if user has paid subscription
    if hasattr(request, 'needs_payment') and request.needs_payment:
        return redirect('payment_modal')
    
    try:
        subscription = request.subscription
        context = {
            'user': request.user,
            'subscription': subscription,
            'plan': subscription.plan if subscription else None,
            'trial_days_remaining': subscription.get_trial_days_remaining() if subscription else 0,
        }
        return render(request, 'core/dashboard.html', context)
    except Exception as e:
        messages.error(request, f"Error loading dashboard: {str(e)}")
        return redirect('payment_modal')


@login_required
def payment_modal(request):
    """
    Payment modal view for unpaid users
    """
    try:
        # Get available plans
        plans = Plan.objects.filter(status='active').order_by('sort_order')
        
        # Get user's subscription
        subscription = getattr(request, 'subscription', None)
        if not subscription:
            subscription = Subscription.objects.filter(user=request.user).first()
        
        # Get intended URL from session
        intended_url = request.session.get('intended_url', reverse('dashboard'))
        
        context = {
            'plans': plans,
            'subscription': subscription,
            'intended_url': intended_url,
            'trial_days_remaining': subscription.get_trial_days_remaining() if subscription else 0,
        }
        
        return render(request, 'core/payment_modal.html', context)
    except Exception as e:
        messages.error(request, f"Error loading payment page: {str(e)}")
        return render(request, 'core/payment_modal.html', {'plans': [], 'error': str(e)})


@login_required
@require_http_methods(["POST"])
def start_trial(request):
    """
    Start a free trial for a plan
    """
    try:
        data = json.loads(request.body)
        plan_id = data.get('plan_id')
        
        plan = Plan.objects.get(id=plan_id)
        
        # Get or create subscription
        subscription, created = Subscription.objects.get_or_create(
            user=request.user,
            defaults={'status': 'unpaid'}
        )
        
        # Start trial
        subscription.plan = plan
        subscription.status = 'trialing'
        subscription.trial_start = timezone.now()
        subscription.trial_end = timezone.now() + timedelta(days=plan.trial_days)
        subscription.current_period_start = timezone.now()
        subscription.current_period_end = subscription.trial_end
        subscription.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Trial started for {plan.name}',
            'trial_days': plan.trial_days,
            'redirect_url': request.session.get('intended_url', reverse('dashboard'))
        })
        
    except Plan.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Plan not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def process_payment(request):
    """
    Process payment for a plan
    """
    try:
        data = json.loads(request.body)
        plan_id = data.get('plan_id')
        billing_cycle = data.get('billing_cycle', 'monthly')
        payment_method_id = data.get('payment_method_id')
        
        plan = Plan.objects.get(id=plan_id)
        amount = plan.get_price_for_cycle(billing_cycle)
        
        # Get or create subscription
        subscription, created = Subscription.objects.get_or_create(
            user=request.user,
            defaults={'status': 'unpaid'}
        )
        
        # Create payment record
        payment = Payment.objects.create(
            user=request.user,
            subscription=subscription,
            amount=amount,
            currency=plan.currency,
            status='pending',
            payment_method='stripe'
        )
        
        # In a real implementation, you would integrate with Stripe here
        # For now, we'll simulate successful payment
        payment.status = 'succeeded'
        payment.save()
        
        # Update subscription
        subscription.plan = plan
        subscription.status = 'active'
        subscription.amount = amount
        subscription.current_period_start = timezone.now()
        
        # Set end date based on billing cycle
        if billing_cycle == 'monthly':
            subscription.current_period_end = timezone.now() + timedelta(days=30)
        elif billing_cycle == 'quarterly':
            subscription.current_period_end = timezone.now() + timedelta(days=90)
        elif billing_cycle == 'annually':
            subscription.current_period_end = timezone.now() + timedelta(days=365)
        elif billing_cycle == 'biennial':
            subscription.current_period_end = timezone.now() + timedelta(days=730)
        
        subscription.save()
        
        # Clear intended URL from session
        if 'intended_url' in request.session:
            del request.session['intended_url']
        
        return JsonResponse({
            'success': True,
            'message': f'Payment successful for {plan.name}',
            'redirect_url': reverse('dashboard')
        })
        
    except Plan.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Plan not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
def check_payment_status(request):
    """
    API endpoint to check payment status
    """
    try:
        subscription = getattr(request, 'subscription', None)
        if not subscription:
            subscription = Subscription.objects.filter(user=request.user).first()
        
        if not subscription:
            return JsonResponse({
                'needs_payment': True,
                'is_paid': False,
                'status': 'no_subscription'
            })
        
        return JsonResponse({
            'needs_payment': subscription.needs_payment(),
            'is_paid': subscription.is_paid(),
            'status': subscription.status,
            'plan': subscription.plan.name if subscription.plan else None,
            'trial_days_remaining': subscription.get_trial_days_remaining(),
            'is_trial_active': subscription.is_trial_active()
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
