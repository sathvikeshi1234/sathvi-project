from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger



from django.contrib.auth import authenticate, login, logout



from django.contrib.auth.decorators import login_required



from django.views.decorators.http import require_POST



from django.views.decorators.csrf import csrf_exempt



from django.contrib.auth.models import User



from django.contrib import messages



from django.db import models
from django.db.models import Q



from django.http import JsonResponse



from django.utils.decorators import method_decorator



from django.views import View



from datetime import datetime



from users.models import Role, UserProfile



from django.utils import timezone



from .models import Company, Plan, SuperAdminSettings, NotificationTemplate, Subscription, Payment, SubscriptionMetrics, Notification



from tickets.models import TicketComment, Ticket











# Helper functions for subscription expiry checking



def check_subscription_expiry(user):
    """Check if user's subscription has expired or is inactive"""
    try:
        from django.utils import timezone
        from users.models import UserProfile
        
        # Get user's company using the same logic as should_show_payment_modal
        profile = getattr(user, 'userprofile', None)
        user_company = None
        
        if profile:
            from superadmin.models import Company
            user_company = Company.objects.filter(users=profile).first()
        
        if not user_company:
            return True  # No company found, show payment modal
        
        # Get most recent subscription for this company
        subscription = user_company.subscriptions.order_by('-created_at').first()
        
        if subscription:
            # If subscription is active or trial, check if it's expired
            if subscription.status in ['active', 'trial']:
                if subscription.end_date and subscription.end_date < timezone.now().date():
                    return True  # Subscription expired
                return False  # Active/Trial subscription not expired
            # If subscription is expired, cancelled, or suspended, show payment modal
            elif subscription.status in ['expired', 'cancelled', 'suspended']:
                return True  # Inactive subscription
            else:
                return False  # Unknown status, don't show modal
        else:
            # No subscription found - show payment modal
            return True
        
    except Exception as e:
        print(f"ERROR: Error checking subscription expiry: {e}")
        import traceback
        traceback.print_exc()
        return False







def should_show_payment_modal(user):
    """
    Comprehensive check to determine if payment modal should be shown
    
    UPDATED: Show payment modal for ADMIN users when subscription is expired/expiring
    UPDATED: Show payment modal for NEW regular users who don't have subscriptions
    """
    try:
        # Check user role to determine modal behavior
        from users.models import UserProfile
        user_role = None
        if hasattr(user, 'userprofile') and getattr(user.userprofile, 'role', None):
            user_role = getattr(user.userprofile.role, 'name', '').lower()
        
        # LOGIC: Show payment modal for:
        # 1. Admin users with expired subscriptions
        # 2. Regular users without any subscription (new users)
        
        is_admin_or_staff = user.is_staff or user.is_superuser
        is_regular_user = user_role in ['user', 'customer']
        
        # Skip for agents - they shouldn't see payment modal
        if user_role == 'agent':
            return False
        
        # Check if user has active subscription or recent completed payment
        from superadmin.models import Payment, Subscription
        
        # Get user's company and check for active subscription
        try:
            profile = getattr(user, 'userprofile', None)
            
            # Find user's company
            user_company = None
            if profile:
                from superadmin.models import Company
                user_company = Company.objects.filter(users=profile).first()
            
            # Check if user has an active subscription
            has_active_subscription = False
            if user_company:
                active_subscription = Subscription.objects.filter(
                    company=user_company,
                    status='active'
                ).first()
                
                if active_subscription:
                    has_active_subscription = True
                
                # Check if user has recent completed payment (within last 30 days)
                recent_payment = Payment.objects.filter(
                    company=user_company,
                    status='completed'
                ).order_by('-created_at').first()
                
                if recent_payment:
                    # Check if payment is within subscription period
                    from django.utils import timezone
                    days_since_payment = (timezone.now().date() - recent_payment.created_at.date()).days
                    if days_since_payment <= 30:  # Grace period of 30 days
                        has_active_subscription = True
                        
        except Exception as e:
            print(f"Error checking user subscription: {e}")
            # Continue to other checks if there's an error

        # DECISION LOGIC:
        # 1. Admin users: Show modal if NO active subscription
        # 2. Regular users: Show modal if NO active subscription (new users)
        # 3. Skip if user has active subscription
        
        if has_active_subscription:
            return False  # Don't show modal if user has active subscription
        
        # Show modal for admin users OR regular users without active subscription
        if is_admin_or_staff or is_regular_user:
            return True
            
        return False  # Default: don't show modal
        
    except Exception as e:
        print(f"ERROR: Error in should_show_payment_modal: {e}")
        import traceback
        traceback.print_exc()
        return False







def is_admin_or_superadmin(user):



    """Check if user is Admin or SuperAdmin"""



    try:



        if not user or not user.is_authenticated:



            return False



        



        # Check if user is SuperAdmin (Django superuser)



        if user.is_superuser:



            return True



        



        # Check if user has Admin or SuperAdmin role



        try:



            profile = user.userprofile



            if profile and profile.role:



                return profile.role.name in ['Admin', 'SuperAdmin']



        except:



            pass



        



        return False



    except:



        return False







def _is_superadmin_user(user):



    if not user or not user.is_authenticated:



        return False







    if user.is_superuser:



        return True







    try:



        profile = UserProfile.objects.get(user=user)



        return profile.role and profile.role.name.lower() == 'superadmin'



    except UserProfile.DoesNotExist:



        return False







def get_role_based_redirect(user):



    """Get appropriate redirect URL based on user role"""



    if _is_superadmin_user(user):



        return 'superadmin:superadmin_dashboard'



    elif is_admin_or_superadmin(user):



        return 'dashboards:admin_dashboard'



    else:



        return 'superadmin:superadmin_login'











def get_user_plan_name(user):



    """Get user's current plan name"""



    try:



        companies = Company.objects.all()



        for company in companies:



            if company.name == f'{user.username} Company':



                subscription = company.subscriptions.filter(status='trial').first()



                if subscription and subscription.plan:



                    return subscription.plan.name



        return "Trial"



    except:



        return "Trial"











def get_expiry_date(user):



    """Get subscription expiry date"""



    try:



        companies = Company.objects.all()



        for company in companies:



            if company.name == f'{user.username} Company':



                subscription = company.subscriptions.filter(status='trial').first()



                if subscription:



                    return subscription.end_date.strftime('%B %d, %Y')



        return None



    except:



        return None











def get_days_expired(user):



    """Get days since expiry"""



    try:



        companies = Company.objects.all()



        for company in companies:



            if company.name == f'{user.username} Company':



                subscription = company.subscriptions.filter(status='trial').first()



                if subscription:



                    today = timezone.now().date()



                    if subscription.end_date < today:



                        return (today - subscription.end_date).days



        return 0



    except:



        return 0











# Notification management functions



def create_system_notification(title, message, priority='medium', user=None, expires_in_hours=24):



    """Create a system notification"""



    return Notification.create_notification(



        title=title,



        message=message,



        notification_type='system',



        priority=priority,



        user=user,



        expires_in_hours=expires_in_hours



    )











def create_payment_notification(title, message, priority='medium', user=None, action_url=None):



    """Create a payment-related notification"""



    return Notification.create_notification(



        title=title,



        message=message,



        notification_type='payment',



        priority=priority,



        user=user,



        action_url=action_url,



        action_text='View Payment',



        expires_in_hours=48



    )











def create_subscription_notification(title, message, priority='medium', user=None, action_url=None):



    """Create a subscription-related notification"""



    return Notification.create_notification(



        title=title,



        message=message,



        notification_type='subscription',



        priority=priority,



        user=user,



        action_url=action_url,



        action_text='View Subscription',



        expires_in_hours=72



    )











def create_user_management_notification(title, message, priority='medium', user=None, action_url=None):



    """Create a user management notification"""



    return Notification.create_notification(



        title=title,



        message=message,



        notification_type='user',



        priority=priority,



        user=user,



        action_url=action_url,



        action_text='View User',



        expires_in_hours=24



    )











def get_notifications_context(user):



    """Get notifications context for templates"""



    notifications = Notification.get_user_notifications(user)[:10]  # Latest 10



    unread_count = Notification.get_unread_count(user)



    



    return {



        'notifications': notifications,



        'unread_count': unread_count,



        'has_notifications': notifications.exists(),



    }











def check_and_create_system_notifications():



    """Check system conditions and create appropriate notifications"""



    try:



        # Check for expiring trials (next 7 days)



        from datetime import timedelta



        upcoming_expiry = timezone.now().date() + timedelta(days=7)



        



        expiring_trials = Subscription.objects.filter(



            status='trial',



            end_date__lte=upcoming_expiry,



            end_date__gte=timezone.now().date()



        )



        



        for subscription in expiring_trials:



            days_left = (subscription.end_date - timezone.now().date()).days



            if days_left <= 3:



                priority = 'urgent'



            elif days_left <= 7:



                priority = 'high'



            else:



                priority = 'medium'



                



            # Check if notification already exists for this subscription



            existing_notification = Notification.objects.filter(



                title__contains=f"Trial expiring for {subscription.company.name}",



                created_at__gte=timezone.now() - timedelta(hours=24)



            ).exists()



            



            if not existing_notification:



                create_subscription_notification(



                    title=f"Trial expiring for {subscription.company.name}",



                    message=f"The trial subscription for {subscription.company.name} will expire in {days_left} days.",



                    priority=priority,



                    action_url=f"/superadmin/companies/{subscription.company.id}/"



                )



        



        # Check for failed payments (last 24 hours)



        recent_failed_payments = Payment.objects.filter(



            status='failed',



            created_at__gte=timezone.now() - timedelta(hours=24)



        )



        



        for payment in recent_failed_payments:



            existing_notification = Notification.objects.filter(



                title__contains=f"Payment failed for {payment.company.name}",



                created_at__gte=timezone.now() - timedelta(hours=12)



            ).exists()



            



            if not existing_notification:



                create_payment_notification(



                    title=f"Payment failed for {payment.company.name}",



                    message=f"A payment of ${payment.amount} for {payment.company.name} has failed.",



                    priority='high',



                    action_url=f"/superadmin/transactions/"



                )



        



        # Check for new user registrations (last 24 hours)



        recent_users = User.objects.filter(



            date_joined__gte=timezone.now() - timedelta(hours=24),



            is_active=True



        )



        



        if recent_users.count() > 0:



            existing_notification = Notification.objects.filter(



                title__contains="New user registrations",



                created_at__gte=timezone.now() - timedelta(hours=12)



            ).exists()



            



            if not existing_notification:



                create_user_management_notification(



                    title="New user registrations",



                    message=f"{recent_users.count()} new users have registered in the last 24 hours.",



                    priority='low',



                    action_url="/superadmin/users/"



                )



    



    except Exception as e:



        print(f"Error creating system notifications: {e}")







@login_required(login_url='superadmin:superadmin_login')



def plan_list(request):



    if not is_admin_or_superadmin(request.user):



        return redirect('superadmin:superadmin_login')







    # Only show the three predefined plans: Basic, Standard, Premium



    ALLOWED_PLANS = ['Basic', 'Standard', 'Premium']



    plans = Plan.objects.filter(



        name__in=ALLOWED_PLANS,



        is_active=True, 



        status='active'



    ).order_by('name')



    
    return render(request, 'superadmin/plans.html', {"plans": plans, "sa_page": "plans"})

@login_required(login_url='superadmin:superadmin_login')
def plan_add(request):
    if not is_admin_or_superadmin(request.user):
        return redirect('superadmin:superadmin_login')
    
    if request.method == 'POST':
        # Handle plan creation logic here
        messages.success(request, 'Plan created successfully!')
        return redirect('superadmin:plans_list')
    
    context = {
        'sa_page': 'plans'
    }
    return render(request, 'superadmin/plan_add.html', context)

@login_required(login_url='superadmin:superadmin_login')
def plan_edit(request, plan_id):
    if not is_admin_or_superadmin(request.user):
        return redirect('superadmin:superadmin_login')
    
    plan = get_object_or_404(Plan, id=plan_id)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        price = request.POST.get('price', '').strip()
        billing_cycle = request.POST.get('billing_cycle', 'monthly')
        users = request.POST.get('users', '5')
        storage = request.POST.get('storage', '10GB')
        features = request.POST.getlist('features', [])
        
        if not name or not price:
            messages.error(request, 'Plan name and price are required.')
        else:
            try:
                plan.name = name
                plan.price = price
                plan.billing_cycle = billing_cycle
                plan.users = int(users) if users != '999' else 999
                plan.storage = storage
                plan.features = features
                plan.save()
                messages.success(request, f'Plan "{name}" updated successfully!')
                return redirect('superadmin:plans_list')
            except Exception as e:
                messages.error(request, f'Error updating plan: {str(e)}')
    
    context = {
        'plan': plan,
        'sa_page': 'plans'
    }
    return render(request, 'superadmin/plan_edit.html', context)

@login_required(login_url='superadmin:superadmin_login')
def companies_list(request):
    if not is_admin_or_superadmin(request.user):
        return redirect('superadmin:superadmin_login')
    
    companies = Company.objects.all().order_by('-created_at')
    
    # Pagination: 7 companies per page
    paginator = Paginator(companies, 7)
    page = request.GET.get('page')
    
    try:
        companies = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        companies = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page
        companies = paginator.page(paginator.num_pages)
    
    context = {
        'companies': companies,
        'sa_page': 'companies'
    }
    
    # Handle AJAX request for partial refresh
    if request.GET.get('ajax') == '1':
        return render(request, 'superadmin/companies_list_partial.html', context)
    
    return render(request, 'superadmin/companies.html', context)

@login_required(login_url='superadmin:superadmin_login')
def company_create(request):
    if not is_admin_or_superadmin(request.user):
        return redirect('superadmin:superadmin_login')
    
    if request.method == 'POST':
        # Handle AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                # Get form data
                name = request.POST.get('name', '').strip()
                email = request.POST.get('email', '').strip()
                phone = request.POST.get('phone', '').strip()
                address = request.POST.get('address', '').strip()
                plan_name = request.POST.get('plan', '')
                subscription_status = request.POST.get('subscription_status', 'trial')
                
                # Validate required fields
                if not name or not email:
                    return JsonResponse({
                        'success': False,
                        'message': 'Company name and email are required.'
                    })
                
                # Validate email format
                import re
                email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
                if not re.match(email_pattern, email):
                    return JsonResponse({
                        'success': False,
                        'message': 'Please enter a valid email address.'
                    })
                
                # Check if email already exists
                if Company.objects.filter(email=email).exists():
                    return JsonResponse({
                        'success': False,
                        'message': 'A company with this email already exists.'
                    })
                
                # Create company
                company = Company.objects.create(
                    name=name,
                    email=email,
                    phone=phone,
                    address=address,
                    subscription_status=subscription_status,
                    is_active=True
                )
                
                # Add plan if specified
                if plan_name:
                    try:
                        plan = Plan.objects.get(name__iexact=plan_name)
                        company.plan = plan
                        company.save()
                    except Plan.DoesNotExist:
                        pass
                
                return JsonResponse({
                    'success': True,
                    'message': f'Company "{name}" created successfully!',
                    'company_id': company.id
                })
                
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': f'Error creating company: {str(e)}'
                })
        else:
            # Handle regular form submission (fallback)
            name = request.POST.get('name', '').strip()
            email = request.POST.get('email', '').strip()
            phone = request.POST.get('phone', '').strip()
            address = request.POST.get('address', '').strip()
            plan_name = request.POST.get('plan', '')
            subscription_status = request.POST.get('subscription_status', 'trial')
            
            if not name or not email:
                messages.error(request, 'Company name and email are required.')
                return redirect('superadmin:companies_list')
            
            company = Company.objects.create(
                name=name,
                email=email,
                phone=phone,
                address=address,
                subscription_status=subscription_status,
                is_active=True
            )
            
            if plan_name:
                try:
                    plan = Plan.objects.get(name__iexact=plan_name)
                    company.plan = plan
                    company.save()
                except Plan.DoesNotExist:
                    pass
            
            messages.success(request, f'Company "{name}" created successfully!')
            return redirect('superadmin:companies_list')
    
    # GET request - render company creation form
    context = {
        'sa_page': 'companies',
        'plans': Plan.objects.all()
    }
    return render(request, 'superadmin/company_add.html', context)

@login_required(login_url='superadmin:superadmin_login')
def company_detail(request, company_id):
    if not is_admin_or_superadmin(request.user):
        return redirect('superadmin:superadmin_login')
    
    company = get_object_or_404(Company, id=company_id)
    
    # Get company subscriptions
    subscriptions = company.subscriptions.select_related('plan').order_by('-created_at')
    
    # Get company users
    users = company.users.select_related('user', 'role').all()
    
    context = {
        'company': company,
        'subscriptions': subscriptions,
        'users': users,
        'sa_page': 'companies'
    }
    
    return render(request, 'superadmin/company_detail.html', context)

@login_required(login_url='superadmin:superadmin_login')
def company_edit(request, company_id):
    if not is_admin_or_superadmin(request.user):
        return redirect('superadmin:superadmin_login')
    
    company = get_object_or_404(Company, id=company_id)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        plan_id = request.POST.get('plan', '')
        subscription_status = request.POST.get('subscription_status', 'trial')
        is_active = request.POST.get('is_active') == 'on'
        
        # Validate required fields
        if not name or not email:
            messages.error(request, 'Name and email are required.')
        else:
            # Update company
            company.name = name
            company.email = email
            company.phone = phone
            company.address = address
            company.subscription_status = subscription_status
            company.is_active = is_active
            
            # Update plan if provided
            if plan_id:
                try:
                    plan = Plan.objects.get(id=plan_id)
                    company.plan = plan
                except Plan.DoesNotExist:
                    pass
            
            company.save()
            messages.success(request, 'Company updated successfully.')
            return redirect('superadmin:companies_list')
    
    context = {
        'company': company,
        'plans': Plan.objects.filter(is_active=True),
        'sa_page': 'companies'
    }
    
    return render(request, 'superadmin/company_edit.html', context)

@login_required(login_url='superadmin:superadmin_login')
def company_delete(request, company_id):
    if not is_admin_or_superadmin(request.user):
        return redirect('superadmin:superadmin_login')
    
    company = get_object_or_404(Company, id=company_id)
    
    if request.method == 'POST':
        company_name = company.name
        company.delete()
        messages.success(request, f'Company "{company_name}" has been deleted successfully.')
        return redirect('superadmin:companies_list')
    
    # For GET requests, show confirmation page
    context = {
        'company': company,
        'sa_page': 'companies'
    }
    return render(request, 'superadmin/company_delete.html', context)

@login_required(login_url='superadmin:superadmin_login')
def subscriptions_list(request):
    if not is_admin_or_superadmin(request.user):
        return redirect('superadmin:superadmin_login')
    
    from .models import Payment
    from django.utils import timezone
    from datetime import timedelta, date
    from decimal import Decimal
    
    subscriptions = Subscription.objects.select_related('company', 'plan').order_by('-created_at')
    payments = Payment.objects.select_related('subscription__plan', 'company').order_by('-payment_date')
    
    # Calculate subscription statistics
    total_subscriptions = subscriptions.count()
    active_subscriptions = subscriptions.filter(status='active').count()
    
    # Calculate monthly revenue (current month)
    current_month_start = timezone.now().date().replace(day=1)
    current_month_payments = payments.filter(
        payment_date__gte=current_month_start,
        status='completed'
    )
    monthly_revenue = current_month_payments.aggregate(
        total=models.Sum('amount')
    )['total'] or Decimal('0.00')
    
    # Calculate MRR (Monthly Recurring Revenue) - sum of active subscription monthly amounts
    mrr = subscriptions.filter(status='active').aggregate(
        total=models.Sum('total_amount')
    )['total'] or Decimal('0.00')
    
    # Calculate churn rate (simplified - cancelled subscriptions this month / total subscriptions)
    current_month_cancellations = subscriptions.filter(
        status='cancelled',
        cancelled_at__gte=current_month_start
    ).count()
    churn_rate = (current_month_cancellations / total_subscriptions * 100) if total_subscriptions > 0 else 0
    
    # Get recent payments
    recent_payments = payments[:5]
    
    # Get all companies for the dropdown
    from .models import Company
    companies = Company.objects.all().order_by('name')
    
    context = {
        'subscriptions': subscriptions,
        'all_subscriptions_list': subscriptions,  # Template expects this variable name
        'total_subscriptions': total_subscriptions,
        'active_subscriptions': active_subscriptions,
        'monthly_revenue': monthly_revenue,
        'mrr': mrr,
        'churn_rate': round(churn_rate, 1),
        'recent_payments': recent_payments,
        'companies': companies,  # Add companies for the dropdown
        'currency_symbol': '₹',  # Default currency symbol
        'sa_page': 'subscriptions'
    }
    
    return render(request, 'superadmin/subscriptions.html', context)


@login_required(login_url='superadmin:superadmin_login')
def payment_create(request):
    """Create a new payment record"""
    if not is_admin_or_superadmin(request.user):
        return redirect('superadmin:superadmin_login')
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)
    
    try:
        from .models import Payment, Company
        from django.utils import timezone
        import uuid
        
        # Get form data
        company_id = request.POST.get('company')
        amount = request.POST.get('amount')
        payment_date = request.POST.get('payment_date')
        payment_method = request.POST.get('payment_method')
        payment_type = request.POST.get('payment_type')
        notes = request.POST.get('notes', '')
        
        # Validate required fields
        if not all([company_id, amount, payment_date, payment_method, payment_type]):
            return JsonResponse({'error': 'All required fields must be filled'}, status=400)
        
        # Get company
        company = get_object_or_404(Company, id=company_id)
        
        # Parse payment date
        from datetime import datetime
        try:
            payment_date_obj = datetime.strptime(payment_date, '%Y-%m-%d')
        except ValueError:
            return JsonResponse({'error': 'Invalid payment date format'}, status=400)
        
        # Create payment
        payment = Payment.objects.create(
            company=company,
            amount=amount,
            payment_method=payment_method,
            payment_type=payment_type,
            payment_date=payment_date_obj,
            status='completed',  # Auto-complete manual payments
            transaction_id=f'MANUAL-{uuid.uuid4().hex[:8].upper()}',
            invoice_number=f'INV-{timezone.now().strftime("%Y%m%d")}-{uuid.uuid4().hex[:6].upper()}',
            notes=notes
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Payment recorded successfully',
            'payment_id': payment.id,
            'transaction_id': payment.transaction_id
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required(login_url='superadmin:superadmin_login')
def subscription_change_plan(request, subscription_id):
    """Handle subscription upgrade/downgrade"""
    if not is_admin_or_superadmin(request.user):
        return redirect('superadmin:superadmin_login')
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)
    
    try:
        from .models import Subscription, Plan
        
        # Get subscription
        subscription = get_object_or_404(Subscription, id=subscription_id)
        
        # Get form data
        new_plan_code = request.POST.get('new_plan')
        new_billing_cycle = request.POST.get('new_billing_cycle')
        effective_date_str = request.POST.get('effective_date')
        
        # Validate required fields
        if not all([new_plan_code, new_billing_cycle, effective_date_str]):
            return JsonResponse({'error': 'All required fields must be filled'}, status=400)
        
        # Parse effective date
        from datetime import datetime
        try:
            effective_date = datetime.strptime(effective_date_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'error': 'Invalid effective date format'}, status=400)
        
        # Map plan codes to actual plans
        plan_mapping = {
            'basic': 'Basic',
            'standard': 'Standard', 
            'premium': 'Premium',
            'enterprise': 'Enterprise'
        }
        
        plan_name = plan_mapping.get(new_plan_code)
        if not plan_name:
            return JsonResponse({'error': 'Invalid plan selected'}, status=400)
        
        # Get the new plan
        new_plan = get_object_or_404(Plan, name=plan_name)
        
        # Calculate new amount based on billing cycle
        base_price = new_plan.price
        if new_billing_cycle == 'quarterly':
            new_amount = base_price * 3
        elif new_billing_cycle == 'yearly':
            new_amount = base_price * 12
        else:  # monthly
            new_amount = base_price
        
        # Store old values for history
        old_plan = subscription.plan
        old_amount = subscription.total_amount
        old_billing_cycle = subscription.billing_cycle
        
        # Update subscription
        subscription.plan = new_plan
        subscription.billing_cycle = new_billing_cycle
        subscription.total_amount = new_amount
        subscription.next_billing_date = effective_date
        
        # Save changes
        subscription.save()
        
        # Create a payment record for the plan change
        from .models import Payment
        import uuid
        from django.utils import timezone
        
        Payment.objects.create(
            company=subscription.company,
            subscription=subscription,
            amount=new_amount - old_amount if new_amount != old_amount else 0,
            payment_method='manual',
            payment_type='upgrade' if new_amount > old_amount else 'refund' if new_amount < old_amount else 'subscription',
            status='completed',
            payment_date=timezone.now(),
            transaction_id=f'PLAN-CHANGE-{uuid.uuid4().hex[:8].upper()}',
            notes=f'Plan changed from {old_plan.name} ({old_billing_cycle}) to {new_plan.name} ({new_billing_cycle})'
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Successfully changed plan to {new_plan.name}',
            'new_plan': new_plan.name,
            'new_amount': f'₹{new_amount:.2f}',
            'new_billing_cycle': new_billing_cycle
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required(login_url='superadmin:superadmin_login')
def subscription_renew(request, subscription_id):
    """Handle subscription renewal"""
    if not is_admin_or_superadmin(request.user):
        return redirect('superadmin:superadmin_login')
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)
    
    try:
        from .models import Subscription, Payment
        from django.utils import timezone
        from datetime import datetime, timedelta
        import uuid
        
        # Get subscription
        subscription = get_object_or_404(Subscription, id=subscription_id)
        
        # Get form data
        billing_cycle = request.POST.get('billing_cycle')
        renewal_date_str = request.POST.get('renewal_date')
        payment_method = request.POST.get('payment_method')
        
        # Validate required fields
        if not all([billing_cycle, renewal_date_str, payment_method]):
            return JsonResponse({'error': 'All required fields must be filled'}, status=400)
        
        # Parse renewal date
        try:
            renewal_date = datetime.strptime(renewal_date_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'error': 'Invalid renewal date format'}, status=400)
        
        # Calculate new billing date based on cycle
        if billing_cycle == 'monthly':
            new_billing_date = renewal_date + timedelta(days=30)
            months = 1
        elif billing_cycle == 'quarterly':
            new_billing_date = renewal_date + timedelta(days=90)
            months = 3
        elif billing_cycle == 'yearly':
            new_billing_date = renewal_date + timedelta(days=365)
            months = 12
        else:
            return JsonResponse({'error': 'Invalid billing cycle'}, status=400)
        
        # Calculate renewal amount based on current plan
        base_price = subscription.plan.price
        if billing_cycle == 'monthly':
            renewal_amount = base_price * 1
        elif billing_cycle == 'quarterly':
            renewal_amount = base_price * 3
        elif billing_cycle == 'yearly':
            renewal_amount = base_price * 12
        else:
            renewal_amount = base_price
        
        # Store old values
        old_billing_date = subscription.next_billing_date
        old_amount = subscription.total_amount
        
        # Update subscription
        subscription.billing_cycle = billing_cycle
        subscription.next_billing_date = new_billing_date
        subscription.total_amount = renewal_amount
        subscription.status = 'active'  # Ensure subscription is active
        subscription.save()
        
        # Create payment record for renewal
        Payment.objects.create(
            company=subscription.company,
            subscription=subscription,
            amount=renewal_amount,
            payment_method=payment_method,
            payment_type='subscription',
            status='completed',
            payment_date=timezone.now(),
            transaction_id=f'RENEWAL-{uuid.uuid4().hex[:8].upper()}',
            invoice_number=f'REN-{timezone.now().strftime("%Y%m%d")}-{uuid.uuid4().hex[:6].upper()}',
            notes=f'Subscription renewed for {months} month(s) from {renewal_date} to {new_billing_date}'
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Subscription successfully renewed for {months} month(s)',
            'new_billing_date': new_billing_date.strftime('%b %d, %Y'),
            'months': months,
            'amount': f'₹{renewal_amount:.2f}'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required(login_url='superadmin:superadmin_login')
def subscription_view(request, subscription_id):
    if not is_admin_or_superadmin(request.user):
        return redirect('superadmin:superadmin_login')
    
    from .models import Payment
    from django.utils import timezone
    
    # Get subscription with related data
    subscription = get_object_or_404(Subscription.objects.select_related('company', 'plan'), id=subscription_id)
    
    # Get payment history for this subscription
    payments = Payment.objects.filter(subscription=subscription).order_by('-payment_date')
    
    # Calculate subscription metrics
    total_paid = payments.filter(status='completed').aggregate(
        total=models.Sum('amount')
    )['total'] or 0
    
    # Get days remaining
    if subscription.end_date and subscription.status == 'active':
        days_remaining = (subscription.end_date - timezone.now().date()).days
    else:
        days_remaining = 0
    
    context = {
        'subscription': subscription,
        'payments': payments,
        'total_paid': total_paid,
        'days_remaining': days_remaining,
        'sa_page': 'subscriptions'
    }
    
    return render(request, 'superadmin/subscription_view.html', context)


@login_required(login_url='superadmin:superadmin_login')
def transaction_details(request, payment_id):
    if not is_admin_or_superadmin(request.user):
        return redirect('superadmin:superadmin_login')
    
    from .models import Payment
    from django.http import JsonResponse
    
    try:
        # Get payment with related data
        payment = get_object_or_404(Payment.objects.select_related('subscription__plan', 'subscription__company', 'company'), id=payment_id)
        
        # Prepare transaction data
        transaction_data = {
            'id': payment.id,
            'amount': str(payment.amount),
            'status': payment.status,
            'payment_date': payment.payment_date.strftime('%Y-%m-%d %H:%M:%S') if payment.payment_date else None,
            'payment_method': payment.payment_method or 'N/A',
            'transaction_id': payment.transaction_id or 'N/A',
            'company': {
                'name': payment.company.name if payment.company else (payment.subscription.company.name if payment.subscription else 'N/A'),
                'email': payment.company.email if payment.company else (payment.subscription.company.email if payment.subscription else 'N/A')
            },
            'subscription': {
                'plan': payment.subscription.plan.name if payment.subscription else 'N/A',
                'status': payment.subscription.status if payment.subscription else 'N/A'
            },
            'created_at': payment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': payment.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return JsonResponse({
            'success': True,
            'transaction': transaction_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@login_required(login_url='superadmin:superadmin_login')
def users_list(request):
    if not is_admin_or_superadmin(request.user):
        return redirect('superadmin:superadmin_login')
    
    users = User.objects.select_related('userprofile__role').order_by('-date_joined')
    
    # Pagination: 7 users per page
    paginator = Paginator(users, 7)
    page = request.GET.get('page')
    
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        users = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page
        users = paginator.page(paginator.num_pages)
    
    # Get all companies for the dropdown
    companies = Company.objects.filter(is_active=True).order_by('name')
    
    context = {
        'users': users,
        'all_companies': companies,
        'sa_page': 'users'
    }
    
    return render(request, 'superadmin/users.html', context)


@login_required(login_url='superadmin:superadmin_login')
def admin_management(request):
    """Admin management page to view and manage admin users"""
    try:
        from users.models import Role, UserProfile
    except ImportError:
        messages.error(request, 'User models not available. Please check app configuration.')
        return redirect('superadmin:superadmin_dashboard')
    
    # Get admin users (only users with Admin role, excluding SuperAdmin users)
    admin_users = User.objects.filter(
        Q(userprofile__role__name='Admin') & 
        ~Q(is_superuser=True)
    ).distinct().order_by('-date_joined')
    
    # Calculate statistics for Admin role users only
    total_admins = admin_users.count()
    active_admins = admin_users.filter(is_active=True).count()
    inactive_admins = total_admins - active_admins
    
    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(admin_users, 10)  # Show 10 admin users per page
    
    try:
        admins = paginator.page(page)
    except PageNotAnInteger:
        admins = paginator.page(1)
    except EmptyPage:
        admins = paginator.page(paginator.num_pages)
    
    context = {
        'admins': admins,
        'total_admins': total_admins,
        'active_admins': active_admins,
        'inactive_admins': inactive_admins,
        'sa_page': 'admin_management'
    }
    
    return render(request, 'superadmin/admin_management.html', context)


def superadmin_login(request):



    # Already authenticated and authorized -> go to appropriate dashboard



    if is_admin_or_superadmin(request.user):



        return redirect(get_role_based_redirect(request.user))







    if request.method == 'POST':



        username_or_email = (request.POST.get('username') or '').strip()



        password = request.POST.get('password') or ''







        # Allow login via username OR email



        lookup_username = username_or_email



        if '@' in username_or_email:



            from django.contrib.auth.models import User as DjangoUser



            email_user = DjangoUser.objects.filter(email=username_or_email).first()



            if email_user:



                lookup_username = email_user.username







        user = authenticate(request, username=lookup_username, password=password)







        if user and is_admin_or_superadmin(user):



            login(request, user)



            



            # Redirect based on user role



            return redirect(get_role_based_redirect(user))







        messages.error(request, 'Invalid credentials or not authorized')







    return render(request, 'superadmin/login.html')











def admin_login(request):



    # Already authenticated and authorized -> go to appropriate dashboard



    if is_admin_or_superadmin(request.user):



        return redirect(get_role_based_redirect(request.user))







    if request.method == 'POST':



        username_or_email = (request.POST.get('username') or '').strip()



        password = request.POST.get('password') or ''







        # Allow login via username OR email



        lookup_username = username_or_email



        if '@' in username_or_email:



            from django.contrib.auth.models import User as DjangoUser



            email_user = DjangoUser.objects.filter(email=username_or_email).first()



            if email_user:



                lookup_username = email_user.username







        user = authenticate(request, username=lookup_username, password=password)







        if user and is_admin_or_superadmin(user):



            login(request, user)



            



            # Redirect based on user role



            return redirect(get_role_based_redirect(user))







        messages.error(request, 'Invalid credentials or not authorized')







    return render(request, 'superadmin/admin_login.html')















def get_recent_comments():
    """Get recent comments with ticket information"""
    return TicketComment.objects.select_related(
        'author', 'ticket'
    ).order_by('-created_at')[:10]


def get_latest_tickets():
    """Get latest tickets with assigned user information"""
    return Ticket.objects.select_related(
        'assigned_to', 'created_by'
    ).order_by('-created_at')[:10]









@login_required(login_url='superadmin:superadmin_login')



def recent_comments_api(request):



    """API endpoint to get recent comments for the dashboard widget"""



    if not _is_superadmin_user(request.user):



        return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=403)



    



    if request.method != 'GET':



        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)



    



    try:



        comments = get_recent_comments()



        comments_data = []



        



        for comment in comments:



            comments_data.append({



                'id': comment.id,



                'content': comment.content,



                'created_at': comment.created_at.strftime('%b %d, %Y %H:%M'),



                'author_name': comment.author.get_full_name() or comment.author.username,



                'author_username': comment.author.username,



                'ticket_id': comment.ticket.id,



                'ticket_title': comment.ticket.title,



                'ticket_ticket_id': comment.ticket.ticket_id,



                'is_internal': comment.is_internal,



                'ticket_url': f'/tickets/{comment.ticket.id}/'



            })



        



        return JsonResponse({



            'success': True,



            'comments': comments_data,



            'count': len(comments_data)



        })



        



    except Exception as e:



        return JsonResponse({'success': False, 'message': str(e)}, status=500)











@login_required(login_url='superadmin:superadmin_login')



def ticket_search_api(request):



    """API endpoint to search tickets for SuperAdmin dashboard"""



    if not _is_superadmin_user(request.user):



        return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=403)



    



    if request.method != 'GET':



        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)



    



    try:



        search_query = request.GET.get('q', '').strip()



        search_type = request.GET.get('type', 'all')  # all, id, title, status, assigned



        



        if not search_query:



            return JsonResponse({



                'success': True,



                'tickets': [],



                'count': 0,



                'message': 'Please enter a search term'



            })



        



        # Start with base queryset



        tickets = Ticket.objects.select_related('created_by', 'assigned_to')



        



        # Apply search based on type



        if search_type == 'id':



            # Search by ticket ID



            tickets = tickets.filter(ticket_id__icontains=search_query)



        elif search_type == 'title':



            # Search by title



            tickets = tickets.filter(title__icontains=search_query)



        elif search_type == 'status':



            # Search by status



            tickets = tickets.filter(status__icontains=search_query)



        elif search_type == 'assigned':



            # Search by assigned user



            tickets = tickets.filter(



                models.Q(assigned_to__username__icontains=search_query) |



                models.Q(assigned_to__first_name__icontains=search_query) |



                models.Q(assigned_to__last_name__icontains=search_query)



            )



        else:



            # Search across multiple fields (default)



            tickets = tickets.filter(



                models.Q(ticket_id__icontains=search_query) |



                models.Q(title__icontains=search_query) |



                models.Q(status__icontains=search_query) |



                models.Q(description__icontains=search_query) |



                models.Q(created_by__username__icontains=search_query) |



                models.Q(assigned_to__username__icontains=search_query)



            )



        



        # Order by most recent first and limit results



        tickets = tickets.order_by('-created_at')[:20]



        



        # Prepare ticket data



        tickets_data = []



        for ticket in tickets:



            tickets_data.append({



                'id': ticket.id,



                'ticket_id': ticket.ticket_id,



                'title': ticket.title,



                'status': ticket.status,



                'priority': ticket.priority,



                'category': ticket.category or 'General',



                'created_at': ticket.created_at.strftime('%b %d, %Y %H:%M'),



                'created_by': ticket.created_by.get_full_name() or ticket.created_by.username,



                'assigned_to': ticket.assigned_to.get_full_name() if ticket.assigned_to else 'Unassigned',



                'url': f'/tickets/{ticket.id}/',



                'status_class': get_status_class(ticket.status),



                'priority_class': get_priority_class(ticket.priority)



            })



        



        return JsonResponse({



            'success': True,



            'tickets': tickets_data,



            'count': len(tickets_data),



            'query': search_query,



            'type': search_type



        })



        



    except Exception as e:



        return JsonResponse({'success': False, 'message': str(e)}, status=500)











def get_status_class(status):



    """Get CSS class for ticket status"""



    status_classes = {



        'Open': 'badge-open',



        'In Progress': 'badge-progress',



        'Resolved': 'badge-resolved',



        'Closed': 'badge-closed'



    }



    return status_classes.get(status, 'badge-closed')











def get_priority_class(priority):



    """Get CSS class for ticket priority"""



    priority_classes = {



        'Low': 'badge-low',



        'Medium': 'badge-medium',



        'High': 'badge-high',



        'Critical': 'badge-critical'



    }



    return priority_classes.get(priority, 'badge-low')











@login_required(login_url='superadmin:superadmin_login')



def superadmin_dashboard(request):



    if not _is_superadmin_user(request.user):



        return redirect('superadmin:superadmin_login')







    # Check and create system notifications



    check_and_create_system_notifications()







    # Get or create user settings for currency



    settings, created = SuperAdminSettings.objects.get_or_create(



        user=request.user,



        defaults={



            'profile_name': request.user.get_full_name(),



            'profile_email': request.user.email,



        }



    )







    # Calculate real-time statistics



    from django.db.models import Sum, Count



    



    # Total companies



    total_companies = Company.objects.filter(is_active=True).count()



    



    # Active users (users who have logged in or have active subscriptions)



    active_users = User.objects.filter(



        is_active=True,



        last_login__isnull=False



    ).count()



    



    # Total active plans (should always be 3 - Basic, Standard, Premium)



    total_plans = Plan.objects.filter(is_active=True, status='active').count()



    



    # Total revenue from successful payments



    total_revenue = Payment.objects.filter(



        status='completed'



    ).aggregate(total=Sum('amount'))['total'] or 0



    



    # Chart data preparation



    from django.db.models import Sum, Count



    from datetime import datetime, timedelta



    import calendar



    



    # Tickets Over Time Chart Data (default: last 30 days)



    tickets_chart_data = []



    tickets_chart_labels = []



    tickets_chart_data_7days = []



    tickets_chart_labels_7days = []



    tickets_chart_data_3months = []



    tickets_chart_labels_3months = []



    



    # Last 30 days data



    for i in range(30):



        date = datetime.now() - timedelta(days=i)



        day_tickets = Ticket.objects.filter(



            created_at__date=date.date()



        ).count()



        tickets_chart_data.insert(0, float(day_tickets))



        tickets_chart_labels.insert(0, date.strftime('%m/%d'))



    



    # Last 7 days data



    for i in range(7):



        date = datetime.now() - timedelta(days=i)



        day_tickets = Ticket.objects.filter(



            created_at__date=date.date()



        ).count()



        tickets_chart_data_7days.insert(0, float(day_tickets))



        tickets_chart_labels_7days.insert(0, date.strftime('%m/%d'))



    



    # Last 3 months data



    for i in range(3):



        month_date = datetime.now() - timedelta(days=30*i)



        month_start = month_date.replace(day=1)



        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)



        



        month_tickets = Ticket.objects.filter(



            created_at__gte=month_start,



            created_at__lte=month_end



        ).count()



        



        tickets_chart_data_3months.insert(0, float(month_tickets))



        tickets_chart_labels_3months.insert(0, calendar.month_abbr[month_start.month])



    



    # Plan Distribution Chart Data



    plan_distribution_data = []



    plan_distribution_labels = []



    



    active_plans = Plan.objects.filter(is_active=True, status='active')



    for plan in active_plans:



        subscription_count = Subscription.objects.filter(



            plan=plan,



            status='active'



        ).count()



        plan_distribution_data.append(subscription_count)



        plan_distribution_labels.append(plan.name)



    



    # Recent transactions (last 10)



    recent_transactions = Payment.objects.select_related('company', 'subscription__plan').order_by('-payment_date')[:10]



    



    # Total tickets
    total_tickets = Ticket.objects.count()
    
    # Latest tickets (last 10)
    latest_tickets = get_latest_tickets()



    



    # Get notifications context



    notifications_context = get_notifications_context(request.user)



    



    context = {



        'total_companies': total_companies,



        'total_users': active_users,



        'total_plans': total_plans,



        'total_tickets': total_tickets,



        'total_revenue': total_revenue,



        'recent_transactions': recent_transactions,



        'recent_comments': latest_tickets,



        'currency_code': settings.currency,



        'currency_symbol': settings.get_currency_symbol_display(),



        # Chart data



        'tickets_chart_data': tickets_chart_data,



        'tickets_chart_labels': tickets_chart_labels,



        'tickets_chart_data_7days': tickets_chart_data_7days,



        'tickets_chart_labels_7days': tickets_chart_labels_7days,



        'tickets_chart_data_3months': tickets_chart_data_3months,



        'tickets_chart_labels_3months': tickets_chart_labels_3months,



        'plan_distribution_data': plan_distribution_data,



        'plan_distribution_labels': plan_distribution_labels,



        **notifications_context  # Add notifications context



    }



    



    return render(request, 'superadmin/dashboard.html', context)











def superadmin_logout(request):



    logout(request)



    return redirect('superadmin:superadmin_login')











def _has_superadmin_any():



    # Check if there is any Django superuser or any profile with SuperAdmin role



    try:



        has_django_su = User.objects.filter(is_superuser=True).exists()



    except Exception:



        has_django_su = False



    try:



        has_role_su = User.objects.filter(userprofile__role__name='SuperAdmin').exists()



    except Exception:



        has_role_su = False



    return has_django_su or has_role_su











@login_required(login_url='superadmin:superadmin_login')
def user_detail(request, user_id):
    if not is_admin_or_superadmin(request.user):
        return redirect('superadmin:superadmin_login')
    
    try:
        user = User.objects.get(id=user_id)
        context = {
            'user': user,
            'sa_page': 'users'
        }
        return render(request, 'superadmin/user_detail.html', context)
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('superadmin:users_list')

@login_required(login_url='superadmin:superadmin_login')
def user_edit(request, user_id):
    if not is_admin_or_superadmin(request.user):
        return redirect('superadmin:superadmin_login')
    
    # Import models at the top to avoid import issues
    try:
        from users.models import Role, UserProfile
    except ImportError:
        messages.error(request, 'User models not available. Please check app configuration.')
        return redirect('superadmin:users_list')
    
    try:
        user = User.objects.get(id=user_id)
        if request.method == 'POST':
            # Get form data
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            username = request.POST.get('username', '').strip()
            email = request.POST.get('email', '').strip()
            role = request.POST.get('role', '').strip()
            is_active_str = request.POST.get('is_active', '').strip()
            
            # Validate required fields
            if not all([first_name, last_name, username, email, role]):
                messages.error(request, 'All required fields must be filled.')
                return redirect('superadmin:user_edit', user_id=user_id)
            
            # Check if username is already taken by another user
            if User.objects.exclude(id=user_id).filter(username=username).exists():
                messages.error(request, 'Username already exists.')
                return redirect('superadmin:user_edit', user_id=user_id)
            
            # Check if email is already taken by another user
            if User.objects.exclude(id=user_id).filter(email=email).exists():
                messages.error(request, 'Email already exists.')
                return redirect('superadmin:user_edit', user_id=user_id)
            
            # Convert is_active to boolean
            is_active = is_active_str.lower() == 'true'
            
            # Update user basic information
            user.first_name = first_name
            user.last_name = last_name
            user.username = username
            user.email = email
            user.is_active = is_active
            user.save()
            
            # Update user role
            try:
                role_obj = Role.objects.get(name=role)
                if hasattr(user, 'userprofile'):
                    user_profile = user.userprofile
                    user_profile.role = role_obj
                    user_profile.save()
                else:
                    # Create user profile if it doesn't exist
                    UserProfile.objects.create(user=user, role=role_obj)
            except Role.DoesNotExist:
                messages.error(request, f'Role "{role}" not found.')
                return redirect('superadmin:user_edit', user_id=user_id)
            except Exception as e:
                messages.error(request, f'Error updating user role: {str(e)}')
                return redirect('superadmin:user_edit', user_id=user_id)
            
            messages.success(request, f'User "{username}" updated successfully.')
            return redirect('superadmin:users_list')
        
        context = {
            'user': user,
            'sa_page': 'users'
        }
        return render(request, 'superadmin/user_edit.html', context)
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('superadmin:users_list')

@login_required(login_url='superadmin:superadmin_login')
def delete_user(request, user_id):
    if not is_admin_or_superadmin(request.user):
        return redirect('superadmin:superadmin_login')
    
    try:
        user = User.objects.get(id=user_id)
        if request.method == 'POST':
            user.delete()
            messages.success(request, f'User "{user.get_full_name() or user.username}" deleted successfully.')
            return redirect('superadmin:users_list')
        
        context = {
            'user': user,
            'sa_page': 'users'
        }
        return render(request, 'superadmin/user_delete.html', context)
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('superadmin:users_list')

def _is_superadmin_user(u):



    if not u or not getattr(u, 'is_authenticated', False):



        return False



    if u.is_superuser:



        return True



    try:



        role_name = getattr(getattr(getattr(u, 'userprofile', None), 'role', None), 'name', '')



        return (role_name.lower() == 'superadmin')



    except Exception:



        return False











def admin_signup(request):



    """Allow users to sign up as Admin (not SuperAdmin)"""



    if request.method == 'POST':



        username = (request.POST.get('username') or '').strip()



        email = (request.POST.get('email') or '').strip()



        password = (request.POST.get('password') or '')



        confirm = (request.POST.get('confirm_password') or '')







        if not username:



            messages.error(request, 'Username is required.')



            return render(request, 'superadmin/admin_signup.html')



        if User.objects.filter(username=username).exists():



            messages.error(request, 'Username already taken.')



            return render(request, 'superadmin/admin_signup.html')



        if email and User.objects.filter(email=email).exists():



            messages.error(request, 'Email already in use.')



            return render(request, 'superadmin/admin_signup.html')



        if not password or password != confirm:



            messages.error(request, 'Passwords do not match.')



            return render(request, 'superadmin/admin_signup.html')







        user = User.objects.create_user(username=username, email=email, password=password)



        # Staff flag helps with admin features



        user.is_staff = True



        user.save()







        # Assign Admin role (not SuperAdmin)



        role, _ = Role.objects.get_or_create(name='Admin')



        profile, created = UserProfile.objects.get_or_create(user=user)



        profile.role = role



        profile.save()







        # Create trial subscription for admin user



        try:



            # Create a company for the admin user



            company, company_created = Company.objects.get_or_create(



                name=f'{username} Company',



                defaults={



                    'email': f'{username}@company.com',



                    'phone': '0000000000',



                    'subscription_status': 'trial',



                    'subscription_start_date': timezone.now().date(),



                    'plan_expiry_date': timezone.now().date() + timezone.timedelta(days=30),



                }



            )



            



            # Get the Basic plan (fixed plan)



            basic_plan = Plan.objects.filter(name='Basic').first()



            if not basic_plan:



                # If Basic plan doesn't exist, create it as a fallback



                basic_plan = Plan.objects.create(



                    name='Basic',



                    price=199,



                    billing_cycle='monthly',



                    users=5,



                    storage='10GB',



                    status='active',



                    is_active=True



                )



            



            # Create trial subscription



            subscription, sub_created = Subscription.objects.get_or_create(



                company=company,



                defaults={



                    'plan': basic_plan,



                    'status': 'trial',



                    'start_date': timezone.now().date(),



                    'end_date': timezone.now().date() + timezone.timedelta(days=30),



                    'next_billing_date': timezone.now().date() + timezone.timedelta(days=30),



                    'base_price': basic_plan.price,



                    'discount_amount': 0.00,



                    'tax_amount': 0.00,



                    'total_amount': basic_plan.price,



                    'auto_renew': True,



                }



            )



            



            if sub_created:



                print(f'Trial subscription created for admin {username} with Basic plan')



            



        except Exception as e:



            print(f'Error creating trial subscription: {e}')







        messages.success(request, 'Admin account created. You can now log in.')



        return redirect('superadmin:admin_login')







    return render(request, 'superadmin/admin_signup.html')











def superadmin_signup(request):



    # Allow creating the FIRST Super Admin if none exist yet.



    # If one exists, only a logged-in Super Admin may create more.



    any_su = _has_superadmin_any()



    if any_su and not _is_superadmin_user(request.user):



        messages.error(request, 'Super Admin already exists. Only a Super Admin can create another.')



        return redirect('superadmin:superadmin_login')







    if request.method == 'POST':



        username = (request.POST.get('username') or '').strip()



        email = (request.POST.get('email') or '').strip()



        password = (request.POST.get('password') or '')



        confirm = (request.POST.get('confirm_password') or '')







        if not username:



            messages.error(request, 'Username is required.')



            return render(request, 'superadmin/signup.html')



        if User.objects.filter(username=username).exists():



            messages.error(request, 'Username already taken.')



            return render(request, 'superadmin/signup.html')



        if email and User.objects.filter(email=email).exists():



            messages.error(request, 'Email already in use.')



            return render(request, 'superadmin/signup.html')



        if not password or password != confirm:



            messages.error(request, 'Passwords do not match.')



            return render(request, 'superadmin/signup.html')







        user = User.objects.create_user(username=username, email=email, password=password)



        # Staff flag helps with admin features; not strictly required for our checks



        user.is_staff = True



        user.save()







        # Assign SuperAdmin role



        role, _ = Role.objects.get_or_create(name='SuperAdmin')



        profile, created = UserProfile.objects.get_or_create(user=user)



        profile.role = role



        profile.save()







        # Create company and trial subscription for SuperAdmin



        try:



            # Create a company for the SuperAdmin



            company, company_created = Company.objects.get_or_create(



                name=f'{username} Company',



                defaults={



                    'email': f'{username}@company.com',



                    'phone': '0000000000',



                    'subscription_status': 'trial',



                    'subscription_start_date': timezone.now().date(),



                    'plan_expiry_date': timezone.now().date() + timezone.timedelta(days=30),



                }



            )



            



            # Get the Basic plan (fixed plan)



            basic_plan = Plan.objects.filter(name='Basic').first()



            if not basic_plan:



                # If Basic plan doesn't exist, create it as a fallback



                basic_plan = Plan.objects.create(



                    name='Basic',



                    price=199,



                    billing_cycle='monthly',



                    users=5,



                    storage='10GB',



                    status='active',



                    is_active=True



                )



            



            # Create trial subscription



            subscription, sub_created = Subscription.objects.get_or_create(



                company=company,



                defaults={



                    'plan': basic_plan,



                    'status': 'trial',



                    'start_date': timezone.now().date(),



                    'end_date': timezone.now().date() + timezone.timedelta(days=30),



                    'next_billing_date': timezone.now().date() + timezone.timedelta(days=30),



                    'base_price': basic_plan.price,



                    'discount_amount': 0.00,



                    'tax_amount': 0.00,



                    'total_amount': basic_plan.price,



                    'auto_renew': True,



                }



            )



            



            if sub_created:



                print(f'Trial subscription created for SuperAdmin {username} with Basic plan')



            



        except Exception as e:



            print(f'Error creating trial subscription for SuperAdmin: {e}')







        messages.success(request, 'Super Admin account created. You can now log in.')



        return redirect('superadmin:superadmin_login')







    return render(request, 'superadmin/signup.html')











@login_required(login_url='superadmin:superadmin_login')



def superadmin_page(request, page: str):



    print(f'[DEBUG] superadmin_page called with method={request.method}, page={page}')



    



    if not is_admin_or_superadmin(request.user):



        return redirect('superadmin:superadmin_login')







    # Normalize page name (remove .html extension if present)



    page_normalized = page.replace('.html', '')
    # Handle settings page
    if page_normalized == 'settings':
        from .models import SuperAdminSettings
        from django.contrib import messages
        
        if request.method == 'POST':
            # Handle form submission
            try:
                # Get or create user settings
                user_settings, created = SuperAdminSettings.objects.get_or_create(
                    user=request.user,
                    defaults={
                        'profile_name': request.user.get_full_name(),
                        'profile_email': request.user.email,
                        'language': 'en',
                        'timezone': 'UTC',
                        'currency': 'USD',
                    }
                )
                
                # Update settings from form data
                user_settings.profile_name = request.POST.get('profile_name', '')
                user_settings.profile_email = request.POST.get('profile_email', '')
                user_settings.profile_phone = request.POST.get('profile_phone', '')
                user_settings.language = request.POST.get('language', 'en')
                user_settings.timezone = request.POST.get('timezone', 'UTC')
                user_settings.currency = request.POST.get('currency', 'USD')
                
                # Company settings
                user_settings.company_logo = request.FILES.get('company_logo', None)
                user_settings.company_name = request.POST.get('company_name', '')
                user_settings.website_url = request.POST.get('website_url', '')
                user_settings.contact_email = request.POST.get('contact_email', '')
                user_settings.contact_phone = request.POST.get('contact_phone', '')
                user_settings.address = request.POST.get('address', '')
                
                # System settings
                user_settings.maintenance_mode = request.POST.get('maintenance_mode') == 'on'
                user_settings.default_ticket_status = request.POST.get('default_ticket_status', 'Open')
                user_settings.default_ticket_priority = request.POST.get('default_ticket_priority', 'Medium')
                user_settings.first_response_hours = request.POST.get('first_response_hours', 24)
                user_settings.resolution_time_hours = request.POST.get('resolution_time_hours', 72)
                
                user_settings.save()
                messages.success(request, 'Settings saved successfully!')
                
            except Exception as e:
                messages.error(request, f'Error saving settings: {str(e)}')
            
            # Redirect back to settings page
            return redirect('superadmin:superadmin_page', page='settings')
        
        # Handle GET request
        user_settings, created = SuperAdminSettings.objects.get_or_create(
            user=request.user,
            defaults={
                'profile_name': request.user.get_full_name(),
                'profile_email': request.user.email,
                'language': 'en',
                'timezone': 'UTC',
                'currency': 'USD',
            }
        )
        
        # Add settings to context for form population
        ctx = {}
        ctx.update({
            'site_settings': user_settings,  # Template expects site_settings
            'LANGUAGE_CHOICES': [  # Template expects LANGUAGE_CHOICES
                ('en', 'English'),
                ('es', 'Spanish'),
                ('fr', 'French'),
                ('de', 'German'),
                ('zh', 'Chinese'),
                ('ja', 'Japanese'),
            ],
            'TIMEZONE_CHOICES': [  # Template expects TIMEZONE_CHOICES
                ('UTC', 'UTC'),
                ('America/New_York', 'Eastern Time'),
                ('America/Chicago', 'Central Time'),
                ('America/Denver', 'Mountain Time'),
                ('America/Los_Angeles', 'Pacific Time'),
                ('Europe/London', 'London'),
                ('Europe/Paris', 'Paris'),
                ('Asia/Tokyo', 'Tokyo'),
                ('Asia/Shanghai', 'Shanghai'),
            ],
            'CURRENCY_CHOICES': [  # Template expects CURRENCY_CHOICES
                ('USD', 'US Dollar'),
                ('EUR', 'Euro'),
                ('GBP', 'British Pound'),
                ('JPY', 'Japanese Yen'),
                ('CNY', 'Chinese Yuan'),
                ('INR', 'Indian Rupee'),
            ],
        })
        
        return render(request, 'superadmin/settings.html', ctx)
    
    # Handle all_transactions page
    elif page_normalized == 'all_transactions':
        from .models import Payment
        from django.core.paginator import Paginator
        
        payments = Payment.objects.select_related('subscription__plan', 'company').order_by('-payment_date')
        
        # Calculate transaction statistics
        total_transactions = payments.count()
        completed_transactions = payments.filter(status='completed').count()
        pending_transactions = payments.filter(status='pending').count()
        failed_transactions = payments.filter(status='failed').count()
        
        # Implement pagination with 5 records per page
        paginator = Paginator(payments, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'payments': page_obj,
            'all_transactions_list': page_obj,  # Template expects this variable name
            'total_transactions': total_transactions,
            'completed_transactions': completed_transactions,
            'pending_transactions': pending_transactions,
            'failed_transactions': failed_transactions,
            'sa_page': 'all_transactions'
        }
        
        return render(request, 'superadmin/all_transactions.html', context)
    
    # Handle all_subscriptions page
    elif page_normalized == 'all_subscriptions':
        from .models import Payment
        from django.utils import timezone
        from datetime import timedelta, date
        from decimal import Decimal
        from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
        
        subscriptions = Subscription.objects.select_related('company', 'plan').order_by('-created_at')
        
        # Pagination: 7 subscriptions per page
        paginator = Paginator(subscriptions, 7)
        page = request.GET.get('page')
        
        try:
            subscriptions = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page
            subscriptions = paginator.page(1)
        except EmptyPage:
            # If page is out of range, deliver last page
            subscriptions = paginator.page(paginator.num_pages)
        
        # Calculate subscription statistics (use all subscriptions for stats, not just current page)
        all_subscriptions_query = Subscription.objects.select_related('company', 'plan').order_by('-created_at')
        total_subscriptions = all_subscriptions_query.count()
        active_subscriptions = all_subscriptions_query.filter(status='active').count()
        trial_subscriptions = all_subscriptions_query.filter(status='trial').count()
        expired_subscriptions = all_subscriptions_query.filter(status='expired').count()
        
        # Calculate monthly revenue (current month)
        current_month_start = timezone.now().date().replace(day=1)
        current_month_payments = Payment.objects.filter(
            payment_date__gte=current_month_start,
            status='completed'
        )
        monthly_revenue = current_month_payments.aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')
        
        # Calculate MRR (Monthly Recurring Revenue) - sum of active subscription monthly amounts
        mrr = all_subscriptions_query.filter(status='active').aggregate(
            total=models.Sum('total_amount')
        )['total'] or Decimal('0.00')
        
        # Calculate churn rate (simplified - cancelled subscriptions this month / total subscriptions)
        current_month_cancellations = all_subscriptions_query.filter(
            status='cancelled',
            cancelled_at__gte=current_month_start
        ).count()
        churn_rate = (current_month_cancellations / total_subscriptions * 100) if total_subscriptions > 0 else 0
        
        # Get recent payments
        recent_payments = Payment.objects.select_related('subscription__plan', 'company').order_by('-payment_date')[:5]
        
        context = {
            'subscriptions': subscriptions,
            'all_subscriptions_list': subscriptions,  # Template expects this variable name
            'total_subscriptions': total_subscriptions,
            'active_subscriptions': active_subscriptions,
            'trial_subscriptions': trial_subscriptions,
            'expired_subscriptions': expired_subscriptions,
            'monthly_revenue': monthly_revenue,
            'mrr': mrr,
            'churn_rate': round(churn_rate, 1),
            'recent_payments': recent_payments,
            'currency_symbol': '₹',  # Default currency symbol
            'sa_page': 'all_subscriptions'
        }
        
        return render(request, 'superadmin/all_subscriptions.html', context)
    
    # Handle profile page
    elif page_normalized == 'profile':
        from .models import SuperAdminSettings
        from django.http import JsonResponse
        
        # Handle POST requests for AJAX calls
        if request.method == 'POST':
            action = request.POST.get('action')
            
            if action == 'save_personal_info':
                # Update user profile information
                request.user.first_name = request.POST.get('first_name', '')
                request.user.last_name = request.POST.get('last_name', '')
                request.user.email = request.POST.get('email', '')
                request.user.save()
                
                # Refresh the user object to get updated data
                request.user.refresh_from_db()
                
                # Update SuperAdminSettings
                user_settings, created = SuperAdminSettings.objects.get_or_create(
                    user=request.user,
                    defaults={
                        'profile_name': request.user.get_full_name(),
                        'profile_email': request.user.email,
                        'language': 'en',
                        'timezone': 'UTC',
                        'currency': 'USD',
                    }
                )
                
                user_settings.profile_phone = request.POST.get('phone', '')
                user_settings.profile_address = request.POST.get('address', '')
                user_settings.save()
                
                return JsonResponse({'success': True, 'message': 'Profile updated successfully'})
            
            elif action == 'upload_profile_picture':
                # Handle profile picture upload
                if 'profile_picture' in request.FILES:
                    user_settings.profile_picture = request.FILES['profile_picture']
                    user_settings.save()
                    return JsonResponse({'success': True, 'message': 'Profile picture updated'})
                else:
                    return JsonResponse({'success': False, 'message': 'No file uploaded'})
            
            elif action == 'remove_profile_picture':
                # Handle profile picture removal
                if user_settings.profile_picture:
                    # Delete the file from storage
                    try:
                        import os
                        from django.conf import settings
                        if user_settings.profile_picture and hasattr(user_settings.profile_picture, 'path'):
                            file_path = user_settings.profile_picture.path
                            if os.path.exists(file_path):
                                os.remove(file_path)
                    except Exception:
                        pass  # Ignore file deletion errors
                    
                    # Clear the profile picture field
                    user_settings.profile_picture = None
                    user_settings.save()
                    return JsonResponse({'success': True, 'message': 'Profile picture removed successfully'})
                else:
                    return JsonResponse({'success': False, 'message': 'No profile picture to remove'})
            
            elif action == 'save_professional_info':
                # Update professional information
                user_settings, created = SuperAdminSettings.objects.get_or_create(
                    user=request.user,
                    defaults={
                        'profile_name': request.user.get_full_name(),
                        'profile_email': request.user.email,
                        'language': 'en',
                        'timezone': 'UTC',
                        'currency': 'USD',
                    }
                )
                
                user_settings.department = request.POST.get('department', '')
                user_settings.role = request.POST.get('role', '')
                user_settings.employee_id = request.POST.get('employee_id', '')
                
                # Handle join_date
                join_date = request.POST.get('join_date', '')
                if join_date:
                    from datetime import datetime
                    try:
                        user_settings.join_date = datetime.strptime(join_date, '%Y-%m-%d').date()
                    except ValueError:
                        pass  # Keep existing value if date is invalid
                
                user_settings.skills = request.POST.get('skills', '')
                user_settings.save()
                
                return JsonResponse({'success': True, 'message': 'Professional information updated successfully'})
            
            else:
                return JsonResponse({'success': False, 'message': 'Invalid action'})
        
        # Handle GET requests
        user_settings, created = SuperAdminSettings.objects.get_or_create(
            user=request.user,
            defaults={
                'profile_name': request.user.get_full_name(),
                'profile_email': request.user.email,
                'language': 'en',
                'timezone': 'UTC',
                'currency': 'USD',
            }
        )
        
        context = {
            'user': request.user,
            'profile_settings': user_settings,
            'sa_page': 'profile'
        }
        
        return render(request, 'superadmin/profile.html', context)
    
    # Default case - return 404 or redirect
    else:
        return render(request, 'superadmin/404.html', status=404)


@login_required(login_url='superadmin:superadmin_login')
def get_notifications_api(request):
    """API endpoint to get notifications for the current user"""
    if not is_admin_or_superadmin(request.user):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    try:
        # Get notifications for the user
        notifications = Notification.get_user_notifications(request.user)
        
        # Format notifications for frontend
        formatted_notifications = []
        for notification in notifications:
            # Calculate time ago
            time_diff = timezone.now() - notification.created_at
            if time_diff.total_seconds() < 60:
                time_ago = f"{int(time_diff.total_seconds())} seconds ago"
            elif time_diff.total_seconds() < 3600:
                time_ago = f"{int(time_diff.total_seconds() / 60)} minutes ago"
            elif time_diff.total_seconds() < 86400:
                time_ago = f"{int(time_diff.total_seconds() / 3600)} hours ago"
            else:
                time_ago = f"{int(time_diff.total_seconds() / 86400)} days ago"
            
            # Map notification type to icon and color
            icon_map = {
                'info': 'bi-info-circle',
                'success': 'bi-check-circle',
                'warning': 'bi-exclamation-triangle',
                'error': 'bi-x-circle',
                'system': 'bi-gear',
                'payment': 'bi-credit-card',
                'subscription': 'bi-box-arrow-in-right',
                'user': 'bi-person'
            }
            
            color_map = {
                'info': '#3b82f6',
                'success': '#10b981',
                'warning': '#f59e0b',
                'error': '#ef4444',
                'system': '#6b7280',
                'payment': '#f59e0b',
                'subscription': '#8b5cf6',
                'user': '#10b981'
            }
            
            formatted_notifications.append({
                'id': notification.id,
                'type': notification.notification_type,
                'title': notification.title,
                'message': notification.message,
                'time': time_ago,
                'timestamp': notification.created_at.isoformat(),
                'unread': not notification.is_read,
                'priority': notification.priority in ['high', 'urgent'],
                'icon': icon_map.get(notification.notification_type, 'bi-bell'),
                'color': color_map.get(notification.notification_type, '#6b7280'),
                'action_url': notification.action_url,
                'action_text': notification.action_text
            })
        
        # Get unread count
        unread_count = Notification.get_user_notifications(request.user, unread_only=True).count()
        
        return JsonResponse({
            'success': True,
            'notifications': formatted_notifications,
            'unread_count': unread_count
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required(login_url='superadmin:superadmin_login')
@require_POST
def mark_notification_read(request, notification_id):
    """Mark a specific notification as read"""
    if not is_admin_or_superadmin(request.user):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    try:
        notification = get_object_or_404(
            Notification, 
            id=notification_id,
            is_active=True
        )
        
        # Check if notification belongs to user or is broadcast
        if notification.user and notification.user != request.user:
            return JsonResponse({'error': 'Forbidden'}, status=403)
        
        notification.mark_as_read()
        
        return JsonResponse({
            'success': True,
            'message': 'Notification marked as read'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required(login_url='superadmin:superadmin_login')
@require_POST
def delete_notification(request, notification_id):
    """Delete a specific notification"""
    if not is_admin_or_superadmin(request.user):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    try:
        notification = get_object_or_404(
            Notification, 
            id=notification_id,
            is_active=True
        )
        
        # Check if notification belongs to user or is broadcast
        if notification.user and notification.user != request.user:
            return JsonResponse({'error': 'Forbidden'}, status=403)
        
        notification.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Notification deleted successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required(login_url='superadmin:superadmin_login')
@require_POST
def mark_all_notifications_read(request):
    """Mark all notifications as read for the current user"""
    if not is_admin_or_superadmin(request.user):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    try:
        # Get all unread notifications for the user
        unread_notifications = Notification.get_user_notifications(request.user, unread_only=True)
        
        # Mark all as read
        count = 0
        for notification in unread_notifications:
            notification.mark_as_read()
            count += 1
        
        return JsonResponse({
            'success': True,
            'message': f'Marked {count} notifications as read',
            'count': count
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
