"""
Payments views for handling payment processing, subscriptions, and billing
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db import transaction
from django.urls import reverse
from django.conf import settings
from decimal import Decimal
import json
import logging
import razorpay

from superadmin.models import Company, Plan, Subscription, Payment
from users.models import UserProfile

logger = logging.getLogger(__name__)

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


@login_required(login_url='superadmin:superadmin_login')
def payment_create(request):
    """Create a new payment for a subscription"""
    if not _is_admin_or_superadmin(request.user):
        return redirect('superadmin:superadmin_login')
    
    if request.method == 'POST':
        try:
            subscription_id = request.POST.get('subscription_id')
            amount = request.POST.get('amount')
            payment_method = request.POST.get('payment_method', 'credit_card')
            
            subscription = get_object_or_404(Subscription, id=subscription_id)
            
            # Create payment record
            payment = Payment.objects.create(
                subscription=subscription,
                amount=Decimal(amount),
                payment_method=payment_method,
                status='pending',
                payment_date=timezone.now().date(),
                transaction_id=f"TXN_{timezone.now().strftime('%Y%m%d%H%M%S')}"
            )
            
            messages.success(request, 'Payment created successfully')
            return redirect('superadmin:payment_detail', payment_id=payment.id)
            
        except Exception as e:
            messages.error(request, f'Error creating payment: {e}')
            return redirect('superadmin:payments_list')
    
    # GET request - show payment form
    subscription_id = request.GET.get('subscription_id')
    subscription = get_object_or_404(Subscription, id=subscription_id) if subscription_id else None
    
    context = {
        'subscription': subscription,
        'payment_methods': Payment.PAYMENT_METHOD_CHOICES,
    }
    return render(request, 'superadmin/payments/payment_form.html', context)


@login_required(login_url='superadmin:superadmin_login')
def payment_process(request, subscription_id):
    """Process payment for expired trial or subscription"""
    if not _is_admin_or_superadmin(request.user):
        return redirect('superadmin:superadmin_login')
    
    subscription = get_object_or_404(Subscription, id=subscription_id)
    
    if request.method == 'POST':
        try:
            # Get payment details from form
            plan_id = request.POST.get('plan_id')
            payment_method = request.POST.get('payment_method')
            card_number = request.POST.get('card_number')
            card_expiry = request.POST.get('card_expiry')
            card_cvv = request.POST.get('card_cvv')
            card_holder = request.POST.get('card_holder')
            
            # Get the selected plan
            plan = get_object_or_404(Plan, id=plan_id)
            
            # Process payment (in real implementation, integrate with payment gateway)
            with transaction.atomic():
                # Create payment record
                payment = Payment.objects.create(
                    subscription=subscription,
                    amount=plan.price,
                    payment_method=payment_method,
                    status='completed',
                    payment_date=timezone.now().date(),
                    transaction_id=f"TXN_{timezone.now().strftime('%Y%m%d%H%M%S')}",
                    card_last_four=card_number[-4:] if card_number else None,
                    card_holder_name=card_holder
                )
                
                # Update subscription
                subscription.plan = plan
                subscription.status = 'active'
                subscription.start_date = timezone.now().date()
                
                # Set end date based on billing cycle
                if plan.billing_cycle == 'monthly':
                    subscription.end_date = timezone.now().date() + timezone.timedelta(days=30)
                else:  # yearly
                    subscription.end_date = timezone.now().date() + timezone.timedelta(days=365)
                
                subscription.next_billing_date = subscription.end_date
                subscription.base_price = plan.price
                subscription.total_amount = plan.price
                subscription.save()
                
                # Update company subscription status
                company = subscription.company
                company.subscription_status = 'active'
                company.plan = plan
                company.plan_expiry_date = subscription.end_date
                company.save()
                
                messages.success(request, f'Payment successful! Your {plan.name} subscription is now active.')
                return redirect('superadmin:superadmin_dashboard')
                
        except Exception as e:
            logger.error(f"Payment processing error: {e}")
            messages.error(request, f'Payment processing failed: {e}')
    
    # Get available plans
    plans = Plan.objects.filter(is_active=True, status='active').order_by('price')
    
    context = {
        'subscription': subscription,
        'plans': plans,
        'payment_methods': Payment.PAYMENT_METHOD_CHOICES,
        'expiry_info': {
            'days_expired': (timezone.now().date() - subscription.end_date).days if subscription.end_date < timezone.now().date() else 0
        }
    }
    return render(request, 'superadmin/payments/payment_process.html', context)


@login_required(login_url='superadmin:superadmin_login')
def payment_detail(request, payment_id):
    """View payment details"""
    if not _is_admin_or_superadmin(request.user):
        return redirect('superadmin:superadmin_login')
    
    payment = get_object_or_404(Payment, id=payment_id)
    
    context = {
        'payment': payment,
        'subscription': payment.subscription,
        'company': payment.subscription.company,
    }
    return render(request, 'superadmin/payments/payment_detail.html', context)


@login_required(login_url='superadmin:superadmin_login')
def payments_list(request):
    """List all payments"""
    if not _is_admin_or_superadmin(request.user):
        return redirect('superadmin:superadmin_login')
    
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')
    
    payments = Payment.objects.all().select_related('subscription', 'subscription__company', 'subscription__plan')
    
    # Apply filters
    if status_filter:
        payments = payments.filter(status=status_filter)
    
    if date_filter:
        try:
            filter_date = timezone.datetime.strptime(date_filter, '%Y-%m-%d').date()
            payments = payments.filter(payment_date=filter_date)
        except ValueError:
            pass
    
    # Order by most recent
    payments = payments.order_by('-payment_date', '-created_at')
    
    # Calculate totals
    total_amount = payments.aggregate(total=models.Sum('amount'))['total'] or 0
    completed_amount = payments.filter(status='completed').aggregate(total=models.Sum('amount'))['total'] or 0
    
    context = {
        'payments': payments,
        'status_choices': Payment.STATUS_CHOICES,
        'payment_methods': Payment.PAYMENT_METHOD_CHOICES,
        'total_amount': total_amount,
        'completed_amount': completed_amount,
        'status_filter': status_filter,
        'date_filter': date_filter,
    }
    return render(request, 'superadmin/payments/payments_list.html', context)


@login_required(login_url='superadmin:superadmin_login')
def payment_update_status(request, payment_id):
    """Update payment status (for admin use)"""
    if not _is_admin_or_superadmin(request.user):
        return redirect('superadmin:superadmin_login')
    
    payment = get_object_or_404(Payment, id=payment_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        notes = request.POST.get('notes', '')
        
        if new_status in dict(Payment.STATUS_CHOICES).keys():
            payment.status = new_status
            payment.notes = notes
            payment.save()
            
            # If payment is completed, update subscription
            if new_status == 'completed':
                subscription = payment.subscription
                subscription.status = 'active'
                subscription.save()
                
                company = subscription.company
                company.subscription_status = 'active'
                company.save()
            
            messages.success(request, f'Payment status updated to {new_status}')
        else:
            messages.error(request, 'Invalid status')
    
    return redirect('superadmin:payment_detail', payment_id=payment_id)


@csrf_exempt
def payment_webhook(request):
    """Handle payment gateway webhooks (for future integration)"""
    if request.method == 'POST':
        try:
            # Parse webhook data
            webhook_data = json.loads(request.body)
            
            # Verify webhook signature (implementation depends on payment gateway)
            # signature = request.headers.get('X-Signature')
            # if not verify_webhook_signature(webhook_data, signature):
            #     return HttpResponse('Invalid signature', status=401)
            
            # Process webhook based on event type
            event_type = webhook_data.get('event_type')
            
            if event_type == 'payment.completed':
                payment_id = webhook_data.get('payment_id')
                payment = Payment.objects.get(transaction_id=payment_id)
                payment.status = 'completed'
                payment.save()
                
                # Update subscription
                subscription = payment.subscription
                subscription.status = 'active'
                subscription.save()
                
            elif event_type == 'payment.failed':
                payment_id = webhook_data.get('payment_id')
                payment = Payment.objects.get(transaction_id=payment_id)
                payment.status = 'failed'
                payment.save()
            
            return HttpResponse('Webhook processed', status=200)
            
        except Exception as e:
            logger.error(f"Webhook processing error: {e}")
            return HttpResponse('Webhook processing failed', status=400)
    
    return HttpResponse('Method not allowed', status=405)


def _is_admin_or_superadmin(user):
    """Check if user is Admin or SuperAdmin"""
    if not user or not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    try:
        profile = user.userprofile
        if profile and profile.role:
            return profile.role.name in ['Admin', 'SuperAdmin']
    except:
        pass
    
    return False


@login_required(login_url='superadmin:superadmin_login')
def subscription_payments(request, subscription_id):
    """View all payments for a specific subscription"""
    if not _is_admin_or_superadmin(request.user):
        return redirect('superadmin:superadmin_login')
    
    subscription = get_object_or_404(Subscription, id=subscription_id)
    payments = Payment.objects.filter(subscription=subscription).order_by('-payment_date')
    
    context = {
        'subscription': subscription,
        'company': subscription.company,
        'payments': payments,
        'total_paid': payments.filter(status='completed').aggregate(total=models.Sum('amount'))['total'] or 0,
    }
    return render(request, 'superadmin/payments/subscription_payments.html', context)


@login_required(login_url='superadmin:superadmin_login')
def payment_receipt(request, payment_id):
    """Generate payment receipt"""
    if not _is_admin_or_superadmin(request.user):
        return redirect('superadmin:superadmin_login')
    
    payment = get_object_or_404(Payment, id=payment_id)
    
    context = {
        'payment': payment,
        'subscription': payment.subscription,
        'company': payment.subscription.company,
        'plan': payment.subscription.plan,
    }
    return render(request, 'superadmin/payments/payment_receipt.html', context)


# =============================================
# Razorpay Payment Gateway Integration
# =============================================

@login_required
@csrf_exempt
def razorpay_create_order(request):
    """Create a Razorpay order for payment"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        plan_name = data.get('plan_name', '').lower()
        amount = int(data.get('amount', 0))
        
        if not plan_name or not amount:
            return JsonResponse({'success': False, 'error': 'Plan name and amount are required'}, status=400)
        
        # Convert amount to paise (Razorpay uses smallest currency unit)
        amount_in_paise = amount * 100
        
        # Get user's company and subscription
        user_profile = getattr(request.user, 'userprofile', None)
        company = None
        subscription = None
        
        if user_profile:
            # Get the company associated with this user
            company = Company.objects.filter(users=user_profile).first()
            if company:
                subscription = Subscription.objects.filter(company=company).order_by('-created_at').first()
        
        # Create Razorpay order
        order_data = {
            'amount': amount_in_paise,
            'currency': 'INR',
            'receipt': f'order_{timezone.now().strftime("%Y%m%d%H%M%S")}_{request.user.id}',
            'notes': {
                'plan_name': plan_name,
                'user_id': str(request.user.id),
                'company_id': str(company.id) if company else '',
                'subscription_id': str(subscription.id) if subscription else ''
            }
        }
        
        razorpay_order = razorpay_client.order.create(data=order_data)
        
        logger.info(f"Razorpay order created: {razorpay_order['id']} for user {request.user.id}")
        
        return JsonResponse({
            'success': True,
            'order_id': razorpay_order['id'],
            'amount': amount_in_paise,
            'currency': 'INR',
            'key_id': settings.RAZORPAY_KEY_ID,
            'user_name': request.user.get_full_name() or request.user.username,
            'user_email': request.user.email,
            'company_name': company.name if company else 'Your Company'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f"Razorpay order creation failed: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@csrf_exempt
def razorpay_verify_payment(request):
    """Verify Razorpay payment signature and activate subscription"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_signature = data.get('razorpay_signature')
        plan_name = data.get('plan_name', '').lower()
        amount = int(data.get('amount', 0))
        
        if not all([razorpay_payment_id, razorpay_order_id, razorpay_signature]):
            return JsonResponse({'success': False, 'error': 'Missing payment details'}, status=400)
        
        # Verify signature
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }
        
        try:
            razorpay_client.utility.verify_payment_signature(params_dict)
        except razorpay.errors.SignatureVerificationError:
            logger.error(f"Razorpay signature verification failed for order: {razorpay_order_id}")
            return JsonResponse({'success': False, 'error': 'Payment verification failed'}, status=400)
        
        # Payment verified - update subscription and create payment record
        with transaction.atomic():
            user_profile = getattr(request.user, 'userprofile', None)
            company = None
            subscription = None
            
            if user_profile:
                company = Company.objects.filter(users=user_profile).first()
                if company:
                    subscription = Subscription.objects.filter(company=company).order_by('-created_at').first()
            
            # Get or create plan based on plan_name
            plan = Plan.objects.filter(name__iexact=plan_name, is_active=True).first()
            if not plan:
                plan = Plan.objects.filter(is_active=True).first()
            
            # If no plan exists, create a default one
            if not plan:
                plan = Plan.objects.create(
                    name=plan_name.title(),
                    price=Decimal(str(amount)),
                    billing_cycle='monthly',
                    users=10,
                    storage='10GB',
                    status='active',
                    is_active=True
                )
            
            # Create company if user doesn't have one
            if not company:
                company = Company.objects.create(
                    name=f"{request.user.get_full_name() or request.user.username}'s Company",
                    email=request.user.email or f"{request.user.username}@example.com",
                    phone='',
                    subscription_status='active',
                    plan=plan,
                    plan_expiry_date=timezone.now().date() + timezone.timedelta(days=30)
                )
                # Link user profile to company
                if user_profile:
                    company.users.add(user_profile)
                    company.save()
                logger.info(f"Created new company for user {request.user.id}: {company.name}")
            
            # Create subscription if it doesn't exist
            if not subscription:
                end_date = timezone.now().date() + timezone.timedelta(days=365 if plan.billing_cycle == 'yearly' else 30)
                subscription = Subscription.objects.create(
                    company=company,
                    plan=plan,
                    status='active',
                    billing_cycle=plan.billing_cycle,
                    start_date=timezone.now().date(),
                    end_date=end_date,
                    next_billing_date=end_date,
                    base_price=Decimal(str(amount)),
                    total_amount=Decimal(str(amount)),
                    auto_renew=True
                )
                logger.info(f"Created new subscription for company {company.id}")
            else:
                # Update existing subscription
                subscription.status = 'active'
                subscription.plan = plan
                subscription.start_date = timezone.now().date()
                
                # Set end date based on billing cycle
                if plan and plan.billing_cycle == 'yearly':
                    subscription.end_date = timezone.now().date() + timezone.timedelta(days=365)
                else:
                    subscription.end_date = timezone.now().date() + timezone.timedelta(days=30)
                
                subscription.next_billing_date = subscription.end_date
                subscription.base_price = Decimal(str(amount))
                subscription.total_amount = Decimal(str(amount))
                subscription.save()
            
            # Update company subscription status
            company.subscription_status = 'active'
            company.plan = plan
            company.plan_expiry_date = subscription.end_date
            company.save()
            
            # Create payment record
            transaction_id = f'RZP_{razorpay_payment_id}'
            payment = Payment.objects.create(
                subscription=subscription,
                company=company,
                amount=Decimal(str(amount)),
                payment_method='razorpay',  # Mark as Razorpay payment
                payment_type='subscription',
                status='completed',
                payment_date=timezone.now(),
                transaction_id=transaction_id,
                invoice_number=f'INV-{timezone.now().strftime("%Y%m%d")}-{razorpay_payment_id[-6:]}',
                gateway_response={
                    'razorpay_payment_id': razorpay_payment_id,
                    'razorpay_order_id': razorpay_order_id,
                    'razorpay_signature': razorpay_signature
                },
                notes=f'Payment for {plan_name.title()} plan via Razorpay',
                created_by=request.user
            )
            
            logger.info(f"Payment verified and recorded: {transaction_id} for user {request.user.id}")
            
            # Set payment_completed flag in Django session to prevent modal from showing again
            request.session['payment_completed'] = True
            request.session['payment_completed_user_id'] = request.user.id
            request.session.modified = True
        
        return JsonResponse({
            'success': True,
            'message': 'Payment verified successfully',
            'transaction_id': transaction_id,
            'plan_name': plan_name.title(),
            'amount': amount
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f"Razorpay payment verification failed: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
def razorpay_webhook(request):
    """Handle Razorpay webhook events"""
    if request.method != 'POST':
        return HttpResponse('Method not allowed', status=405)
    
    try:
        # Verify webhook signature
        webhook_secret = settings.RAZORPAY_WEBHOOK_SECRET
        webhook_signature = request.headers.get('X-Razorpay-Signature', '')
        webhook_body = request.body.decode('utf-8')
        
        try:
            razorpay_client.utility.verify_webhook_signature(
                webhook_body, webhook_signature, webhook_secret
            )
        except razorpay.errors.SignatureVerificationError:
            logger.error("Razorpay webhook signature verification failed")
            return HttpResponse('Invalid signature', status=401)
        
        # Process webhook event
        event_data = json.loads(webhook_body)
        event_type = event_data.get('event')
        
        logger.info(f"Razorpay webhook received: {event_type}")
        
        if event_type == 'payment.captured':
            # Payment was successfully captured
            payment_entity = event_data.get('payload', {}).get('payment', {}).get('entity', {})
            order_id = payment_entity.get('order_id')
            payment_id = payment_entity.get('id')
            
            logger.info(f"Payment captured webhook: order={order_id}, payment={payment_id}")
        
        elif event_type == 'payment.failed':
            # Payment failed
            payment_entity = event_data.get('payload', {}).get('payment', {}).get('entity', {})
            order_id = payment_entity.get('order_id')
            
            logger.warning(f"Payment failed webhook: order={order_id}")
        
        return HttpResponse('Webhook processed', status=200)
        
    except Exception as e:
        logger.error(f"Razorpay webhook processing failed: {str(e)}")
        return HttpResponse('Webhook processing failed', status=400)
