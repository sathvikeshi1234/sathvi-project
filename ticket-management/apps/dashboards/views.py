from django.shortcuts import render, redirect, get_object_or_404

from django.http import JsonResponse, Http404, HttpResponse, HttpResponseForbidden

from django.contrib.auth.decorators import login_required

from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie

from django.utils import timezone

from django.db.models import Q, Count, Avg, F, DurationField, ExpressionWrapper

from django.core.paginator import Paginator

from django.core.exceptions import ValidationError

from django.contrib import messages

from django.urls import reverse

from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash

from tickets.models import Ticket, UserRating, ChatMessage
from tickets.forms import TicketForm, AdminTicketForm
from users.models import UserProfile

import json

import calendar

import csv

import io

import datetime

from rest_framework.views import APIView

from rest_framework.response import Response

from rest_framework import status

from .models import SiteSettings

import base64

from django.core.files.base import ContentFile

import uuid

import logging

logger = logging.getLogger(__name__)

# Custom decorators for role-based access control
def require_admin_role(view_func):
    """Decorator to ensure user has admin role (admin or superadmin)"""
    def wrapper(request, *args, **kwargs):
        if not is_admin_user(request):
            role_name = getattr(request.user.userprofile.role, 'name', 'No profile') if hasattr(request.user, 'userprofile') and getattr(request.user.userprofile, 'role', None) else 'No profile'
            logger.warning(f"Unauthorized access attempt by {request.user.username} (role: {role_name}) to admin-only view: {view_func.__name__}")
            # Redirect appropriate dashboard based on user role
            if is_agent_user(request):
                return redirect('dashboards:agent_dashboard')
            elif is_regular_user(request):
                return redirect('dashboards:user_dashboard')
            else:
                return redirect('users:login')
        return view_func(request, *args, **kwargs)
    return wrapper

def require_agent_role(view_func):
    """Decorator to ensure user has agent role"""
    def wrapper(request, *args, **kwargs):
        if not is_agent_user(request):
            role_name = getattr(request.user.userprofile.role, 'name', 'No profile') if hasattr(request.user, 'userprofile') and getattr(request.user.userprofile, 'role', None) else 'No profile'
            logger.warning(f"Unauthorized access attempt by {request.user.username} (role: {role_name}) to agent-only view: {view_func.__name__}")
            # Redirect appropriate dashboard based on user role
            if is_admin_user(request):
                return redirect('dashboards:admin_dashboard')
            elif is_regular_user(request):
                return redirect('dashboards:user_dashboard')
            else:
                return redirect('users:login')
        return view_func(request, *args, **kwargs)
    return wrapper

def require_user_role(view_func):
    """Decorator to ensure user has regular user role"""
    def wrapper(request, *args, **kwargs):
        if not is_regular_user(request):
            role_name = getattr(request.user.userprofile.role, 'name', 'No profile') if hasattr(request.user, 'userprofile') and getattr(request.user.userprofile, 'role', None) else 'No profile'
            logger.warning(f"Unauthorized access attempt by {request.user.username} (role: {role_name}) to user-only view: {view_func.__name__}")
            # Redirect appropriate dashboard based on user role
            if is_admin_user(request):
                return redirect('dashboards:admin_dashboard')
            elif is_agent_user(request):
                return redirect('dashboards:agent_dashboard')
            else:
                return redirect('users:login')
        return view_func(request, *args, **kwargs)
    return wrapper


# Role validation helper functions
def validate_user_role(request, allowed_roles):
    """
    Validate if user has allowed role
    allowed_roles: list of role names (e.g., ['user', 'customer'])
    """
    if not hasattr(request.user, "userprofile") or not getattr(request.user.userprofile, "role", None):
        return False
    
    user_role = getattr(request.user.userprofile.role, "name", "").lower()
    return user_role in [role.lower() for role in allowed_roles]

def is_admin_user(request):
    """Check if user is admin (admin or superadmin role)"""
    # First check user profile role
    if hasattr(request.user, "userprofile") and getattr(request.user.userprofile, "role", None):
        role_name = getattr(request.user.userprofile.role, "name", "").lower()
        if role_name in ["admin", "superadmin"]:
            return True
    
    # Then check superuser (but not regular staff, as agents are staff)
    if request.user.is_superuser:
        return True
    
    return False

def is_agent_user(request):
    """Check if user is agent"""
    if hasattr(request.user, "userprofile") and getattr(request.user.userprofile, "role", None):
        role_name = getattr(request.user.userprofile.role, "name", "").lower()
        return role_name == "agent"
    return False

def is_regular_user(request):
    """Check if user is regular user/customer"""
    if hasattr(request.user, "userprofile") and getattr(request.user.userprofile, "role", None):
        role_name = getattr(request.user.userprofile.role, "name", "").lower()
        return role_name in ["user", "customer"]
    return False

def test_edit_page(request):
    """Simple test page for edit functionality"""
    try:
        from tickets.models import Ticket
        ticket = Ticket.objects.first()
        
        if request.method == 'GET':
            return render(request, 'test_edit_page.html', {
                'ticket_id': ticket.ticket_id if ticket else 'TEST-001'
            })
        else:
            return HttpResponse("Method not allowed", status=405)
            
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)






@login_required
@require_admin_role
def admin_payment_page(request):

    """Admin payment page view"""

    # Get URL parameters

    from django.http import QueryDict

    plan = request.GET.get('plan', 'basic')

    price = request.GET.get('price', '199')

    

    ctx = {

        'plan': plan,

        'price': price,

        'plan_name': plan.title() if plan else 'Basic',

    }

    

    return render(request, 'admin_payment_page.html', ctx)





@login_required

def user_notifications_api(request):

    user = request.user



    notifications = []



    ticket_qs = (

        Ticket.objects

        .filter(created_by=user)

        .order_by('-updated_at')[:20]

    )

    for t in ticket_qs:

        notifications.append({

            'timestamp': t.updated_at,

            'category': 'tickets',

            'icon': 'fas fa-ticket-alt',

            'is_unread': t.status in ['Open', 'In Progress'],

            'title': 'Ticket update',

            'text': f"Ticket #{t.ticket_id} · {t.title} · status: {t.status}",

            'url': f"/dashboard/user-dashboard/ticket/{t.ticket_id}/",

        })



    chat_qs = (

        ChatMessage.objects

        .select_related('sender')

        .filter(recipient=user)

        .order_by('-created_at')[:20]

    )

    for m in chat_qs:

        notifications.append({

            'timestamp': m.created_at,

            'category': 'system',

            'icon': 'fas fa-comment',

            'is_unread': not m.is_read,

            'title': 'New message',

            'text': f"New message from {m.sender.get_full_name() or m.sender.username}",

            'url': '/dashboard/user-dashboard/chat/',

        })



    notifications.sort(key=lambda n: n['timestamp'], reverse=True)

    top = notifications[:3]

    unread_count = sum(1 for n in notifications if n.get('is_unread'))



    results = []

    for n in top:

        ts = n.get('timestamp')

        results.append({

            'category': n.get('category') or '',

            'icon': n.get('icon') or '',

            'is_unread': bool(n.get('is_unread')),

            'title': n.get('title') or '',

            'text': n.get('text') or '',

            'url': n.get('url') or '',

            'timestamp': ts.isoformat() if ts else None,

            'time_ago': timezone.localtime(ts).strftime('%b %d, %I:%M %p') if ts else '',

        })



    return JsonResponse({'unread_count': unread_count, 'results': results})





@login_required

def faq_search_api(request):

    """Simple FAQ search endpoint used by the frontend FAQ page.

    Searches the same hard-coded FAQ data and returns matching items as JSON.

    """

    q = (request.GET.get('q') or '').strip().lower()

    if len(q) < 3:

        return JsonResponse({'success': True, 'results': []})



    # Prefer DB-backed FAQs if available

    try:

        from .models import Faq

        faq_qs = Faq.objects.filter(is_published=True)

        matches = faq_qs.filter(

            Q(question__icontains=q) | Q(answer__icontains=q)

        ).order_by('order')[:50]



        results = [{'question': f.question, 'answer': f.answer, 'category': f.category} for f in matches]

        return JsonResponse({'success': True, 'results': results})

    except Exception:

        # Fallback to static inline FAQs for projects without migrations applied

        faq_sections = [

            {

                'key': 'getting-started',

                'title': 'Getting Started',

                'items': [

                    {'question': 'How do I create a new ticket?', 'answer': 'Go to the dashboard sidebar and click the "New Ticket" button. Fill in the subject, category, description and optional attachments, then submit.'},

                    {'question': 'How can I see all my tickets?', 'answer': 'Open the Tickets section in the left menu or use the Dashboard counters (Open, In Progress, Resolved) to filter your tickets.'},

                    {'question': 'What information should I include in a ticket?', 'answer': 'Include a clear title, detailed description of the issue, error messages if any, steps to reproduce, and screenshots where possible.'},

                ],

            },

            {

                'key': 'tickets',

                'title': 'Tickets & Statuses',

                'items': [

                    {'question': 'What do the ticket statuses mean?', 'answer': '"Open" means your request is received, "In Progress" means an agent is working on it, "Resolved" means a solution was provided, and "Closed" is finalised after confirmation.'},

                    {'question': 'Can I reopen a resolved ticket?', 'answer': 'If the issue is not fully solved, you can reply in the ticket conversation or create a new ticket referencing the old one.'},

                    {'question': 'How long does it take to get a response?', 'answer': 'Response time depends on priority, but high and critical tickets are usually handled first. You can see SLA information in your ticket details if configured by the admin.'},

                ],

            },

            {

                'key': 'billing',

                'title': 'Billing & Payments',

                'items': [

                    {'question': 'How do I update my billing information?', 'answer': 'Open the Billing or Settings section (if enabled by your organisation) and update your payment method and billing address.'},

                    {'question': 'Where can I download my invoices?', 'answer': 'Invoices are usually available under your Billing or Account section. If you cannot find them, create a billing ticket and our team will help.'},

                ],

            },

            {

                'key': 'account',

                'title': 'Account & Profile',

                'items': [

                    {'question': 'How do I change my password?', 'answer': 'Go to the Profile page in your user dashboard, open the Security or Password section, and follow the steps to change your password.'},

                    {'question': 'Can I update my email or phone number?', 'answer': 'Yes. On the Profile page you can update your contact information. Some fields may be locked depending on your organisation settings.'},

                    {'question': 'How do notification settings work?', 'answer': 'In Settings you can enable or disable email and desktop notifications for ticket updates, chat replies and system announcements.'},

                ],

            },

            {

                'key': 'troubleshooting',

                'title': 'Troubleshooting',

                'items': [

                    {'question': 'I am not receiving email notifications.', 'answer': 'First check your spam folder. Then verify your email address in the Profile page and confirm that email notifications are enabled in Settings.'},

                    {'question': 'The page is not loading correctly.', 'answer': 'Try refreshing the page, clearing your browser cache, or using a different browser. If the problem continues, create a technical ticket.'},

                ],

            },

        ]



        results = []

        for section in faq_sections:

            for item in section.get('items', []):

                q_question = (item.get('question') or '').lower()

                q_answer = (item.get('answer') or '').lower()

                if q in q_question or q in q_answer:

                    results.append({

                        'question': item.get('question'),

                        'answer': item.get('answer'),

                        'category': section.get('key')

                    })



        return JsonResponse({'success': True, 'results': results})





@login_required

def admin_notifications_api(request):

    user = request.user

    is_admin = bool(

        user.is_authenticated and (

            user.is_superuser or user.is_staff or (

                hasattr(user, 'userprofile')

                and getattr(getattr(user.userprofile, 'role', None), 'name', '').lower() in ['admin', 'superadmin']

            )

        )

    )

    if not is_admin:

        return JsonResponse({'detail': 'Forbidden'}, status=403)



    notifications = []



    # Ticket activity (latest updates)

    ticket_qs = Ticket.objects.select_related('created_by').order_by('-updated_at')[:20]

    for t in ticket_qs:

        notifications.append({

            'timestamp': t.updated_at,

            'category': 'tickets',

            'icon': 'bi bi-ticket-detailed',

            'is_unread': t.status in ['Open', 'In Progress'],

            'title': 'Ticket update',

            'text': f"Ticket #{t.ticket_id} · {t.title} · status: {t.status}",

            'url': f"/dashboard/admin-dashboard/ticket/{t.ticket_id}/",

        })



    # Chat messages sent to this admin

    chat_qs = (

        ChatMessage.objects

        .select_related('sender')

        .filter(recipient=user)

        .order_by('-created_at')[:20]

    )

    for m in chat_qs:

        notifications.append({

            'timestamp': m.created_at,

            'category': 'system',

            'icon': 'bi bi-chat-dots',

            'is_unread': not m.is_read,

            'title': 'New message',

            'text': f"New message from {m.sender.get_full_name() or m.sender.username}",

            'url': '/dashboard/admin-dashboard/chat.html',

        })



    notifications.sort(key=lambda n: n['timestamp'], reverse=True)

    top = notifications[:5]

    unread_count = sum(1 for n in notifications if n.get('is_unread'))



    results = []

    for n in top:

        ts = n.get('timestamp')

        results.append({

            'category': n.get('category') or '',

            'icon': n.get('icon') or '',

            'is_unread': bool(n.get('is_unread')),

            'title': n.get('title') or '',

            'text': n.get('text') or '',

            'url': n.get('url') or '',

            'timestamp': ts.isoformat() if ts else None,

            'time_ago': timezone.localtime(ts).strftime('%b %d, %I:%M %p') if ts else '',

        })



    return JsonResponse({'unread_count': unread_count, 'results': results})





@login_required

def agent_notifications_api(request):

    user = request.user



    notifications = []



    # Tickets assigned to this agent (latest updates)

    ticket_qs = (

        Ticket.objects

        .select_related('created_by')

        .filter(assigned_to=user)

        .order_by('-updated_at')[:20]

    )

    for t in ticket_qs:

        notifications.append({

            'timestamp': t.updated_at,

            'category': 'tickets',

            'icon': 'bi bi-ticket-detailed',

            'is_unread': t.status in ['Open', 'In Progress'],

            'title': 'Assigned ticket',

            'text': f"Ticket #{t.ticket_id} · {t.title} · status: {t.status}",

            'url': f"/dashboard/agent-dashboard/ticket/{t.ticket_id}/",

        })



    # Chat messages sent to this agent

    chat_qs = (

        ChatMessage.objects

        .select_related('sender')

        .filter(recipient=user)

        .order_by('-created_at')[:20]

    )

    for m in chat_qs:

        notifications.append({

            'timestamp': m.created_at,

            'category': 'system',

            'icon': 'bi bi-chat-dots',

            'is_unread': not m.is_read,

            'title': 'New message',

            'text': f"New message from {m.sender.get_full_name() or m.sender.username}",

            'url': '/dashboard/agent-dashboard/chat.html',

        })



    notifications.sort(key=lambda n: n['timestamp'], reverse=True)

    top = notifications[:5]

    unread_count = sum(1 for n in notifications if n.get('is_unread'))



    results = []

    for n in top:

        ts = n.get('timestamp')

        results.append({

            'category': n.get('category') or '',

            'icon': n.get('icon') or '',

            'is_unread': bool(n.get('is_unread')),

            'title': n.get('title') or '',

            'text': n.get('text') or '',

            'url': n.get('url') or '',

            'timestamp': ts.isoformat() if ts else None,

            'time_ago': timezone.localtime(ts).strftime('%b %d, %I:%M %p') if ts else '',

        })



    return JsonResponse({'unread_count': unread_count, 'results': results})





@login_required

def user_ticket_rate(request, identifier: str):

    if request.method != 'POST':

        return redirect('dashboards:user_dashboard_page', page='tickets')



    ticket = Ticket.objects.filter(ticket_id=identifier, created_by=request.user).select_related('assigned_to').first()

    if not ticket:

        raise Http404("Ticket not found")



    rating_raw = (request.POST.get('rating') or '').strip()

    title = (request.POST.get('title') or '').strip() or 'Feedback'

    content = (request.POST.get('content') or '').strip()

    recommend_raw = (request.POST.get('recommend') or '').strip().lower()

    recommend = recommend_raw in ['1', 'true', 'yes', 'y', 'on']



    try:

        rating_val = int(rating_raw)

    except (TypeError, ValueError):

        rating_val = 0



    if rating_val < 1:

        rating_val = 1

    if rating_val > 5:

        rating_val = 5



    agent = getattr(ticket, 'assigned_to', None)



    obj, created = UserRating.objects.get_or_create(

        user=request.user,

        ticket_reference=ticket.ticket_id,

        defaults={

            'agent': agent,

            'rating': rating_val,

            'title': title,

            'content': content,

            'recommend': recommend,

        }

    )



    if not created:

        obj.agent = agent

        obj.rating = rating_val

        obj.title = title

        obj.content = content

        obj.recommend = recommend

        obj.save(update_fields=['agent', 'rating', 'title', 'content', 'recommend'])



    return redirect('dashboards:user_dashboard_page', page='tickets')





@login_required

def admin_dashboard(request):

    # ROLE VALIDATION: Only allow admin users to access admin dashboard
    if not is_admin_user(request):
        # Redirect non-admins to appropriate dashboard
        if is_agent_user(request):
            return redirect("dashboards:agent_dashboard")
        elif is_regular_user(request):
            return redirect("dashboards:user_dashboard")
        else:
            return redirect("users:login")



    # Import the expiry checking functions from superadmin

    from superadmin.views import check_subscription_expiry, get_user_plan_name, get_expiry_date, get_days_expired



    # Admin users do not need payment modal - only new users see payment modal
    # Payment modal is disabled for admin dashboard
    show_payment_modal = False
    plan_name = None
    expiry_date = None
    days_expired = None

    



    total_tickets = Ticket.objects.count()

    open_tickets = Ticket.objects.filter(status__iexact='Open').count()

    resolved_today = Ticket.objects.filter(status__iexact='Resolved', updated_at__date=timezone.now().date()).count()



    # Overall customer satisfaction (average rating across all UserRating entries)

    ratings_qs = UserRating.objects.all()

    ratings_total = ratings_qs.count()

    ratings_avg_val = 0.0

    if ratings_total:

        ratings_agg = ratings_qs.aggregate(avg_rating=Avg('rating'))

        ratings_avg_val = float(ratings_agg.get('avg_rating') or 0.0)



    status_defaults = {"Open": 0, "In Progress": 0, "Resolved": 0}

    for row in Ticket.objects.values('status').annotate(c=Count('id')):

        key = row['status']

        if key in status_defaults:

            status_defaults[key] = row['c']

    open_count = status_defaults["Open"]

    in_progress_count = status_defaults["In Progress"]

    resolved_count = status_defaults["Resolved"]

    denom = total_tickets or 1

    open_percent = int((open_count / denom) * 100)

    in_progress_percent = int((in_progress_count / denom) * 100)

    resolved_percent = int((resolved_count / denom) * 100)



    recent_tickets = Ticket.objects.select_related('created_by').order_by('-created_at')[:11]



    # Admin dashboard does not require payment modal logic
    # Payment modal is only for new users, not admin users
    subscription = None



    ctx = {

        "total_tickets": total_tickets,

        "open_tickets": open_tickets,

        "resolved_today": resolved_today,

        "open_percent": open_percent,

        "in_progress_percent": in_progress_percent,

        "resolved_percent": resolved_percent,

        "recent_tickets": recent_tickets,

        "dashboard_avg_rating": round(ratings_avg_val, 1) if ratings_total else None,

        "dashboard_total_ratings": ratings_total,

        "show_payment_modal": show_payment_modal,

        "plan_name": plan_name,

        "expiry_date": expiry_date,

        "days_expired": days_expired,

        "subscription": subscription,  # Add subscription to context

        "razorpay_key": "rzp_test_1DP5mmOlF5G5ag"  # Add Razorpay test key (use your actual key in production)

    }



    return render(request, 'admindashboard/index.html', ctx)





@login_required

def agent_dashboard(request):
    
    # ROLE VALIDATION: Only allow agents to access agent dashboard - STRICT CHECK
    if not is_agent_user(request):
        # Log the unauthorized access attempt
        role_name = getattr(request.user.userprofile.role, 'name', 'No profile') if hasattr(request.user, 'userprofile') and getattr(request.user.userprofile, 'role', None) else 'No profile'
        logger.warning(f"Unauthorized access attempt by {request.user.username} (role: {role_name}) to agent dashboard")
        
        # Redirect appropriate dashboard based on user role
        if is_admin_user(request):
            return redirect("dashboards:admin_dashboard")
        elif is_regular_user(request):
            return redirect("dashboards:user_dashboard")
        else:
            return redirect("users:login")

    """Simple Agent dashboard view rendering the agentdashboard template.



    Access allowed for users whose profile role is 'Agent' or staff agents.

    """

    user = request.user



    # Tickets assigned to this agent

    assigned_qs = Ticket.objects.filter(assigned_to=user)

    today = timezone.now().date()



    # Key stats for the top cards

    my_open_tickets = assigned_qs.filter(status__in=['Open', 'In Progress']).count()

    due_today = assigned_qs.filter(status__in=['Open', 'In Progress'], created_at__date=today).count()



    # Unread replies from ChatMessage model (direct messages to this agent)

    unread_replies = ChatMessage.objects.filter(recipient=user, is_read=False).count()



    # Simple SLA-at-risk approximation: high/critical priority still not resolved

    sla_at_risk = assigned_qs.filter(

        status__in=['Open', 'In Progress'],

        priority__in=['High', 'Critical'],

    ).count()



    # Recent tickets assigned to this agent

    recent_assigned = assigned_qs.select_related('created_by').order_by('-created_at')[:5]



    # Tickets considered "at risk" for the SLA section

    sla_tickets = assigned_qs.filter(

        status__in=['Open', 'In Progress'],

        priority__in=['High', 'Critical'],

    ).order_by('created_at')[:5]



    # Basic performance metrics based on this agent's tickets

    avg_first_response_display = "0m 0s"

    resolved_today = assigned_qs.filter(

        status__in=['Resolved', 'Closed'],

        updated_at__date=today,

    ).count()



    resolved_qs = assigned_qs.filter(status__in=['Resolved', 'Closed'])

    if resolved_qs.exists():

        duration_expr = ExpressionWrapper(

            F('updated_at') - F('created_at'),

            output_field=DurationField(),

        )

        agg = resolved_qs.aggregate(avg_duration=Avg(duration_expr))

        avg_duration = agg.get('avg_duration')

        if avg_duration is not None:

            total_seconds = int(avg_duration.total_seconds())

            minutes = (total_seconds % 3600) // 60

            seconds = total_seconds % 60

            avg_first_response_display = f"{minutes}m {seconds}s"



    # Customer satisfaction from UserRating entries for this agent

    ratings_qs = UserRating.objects.filter(agent=user)

    ratings_total = ratings_qs.count()

    satisfaction_display = "0.0/5"

    if ratings_total:

        ratings_agg = ratings_qs.aggregate(avg_rating=Avg('rating'))

        avg_val = float(ratings_agg.get('avg_rating') or 0.0)

        satisfaction_display = f"{round(avg_val, 1)}/5"



    ctx = {

        'agent_my_open_tickets': my_open_tickets,

        'agent_due_today': due_today,

        'agent_unread_replies': unread_replies,

        'agent_sla_at_risk': sla_at_risk,

        'agent_recent_assigned': recent_assigned,

        'agent_sla_tickets': sla_tickets,

        'agent_avg_first_response_display': avg_first_response_display,

        'agent_resolved_today': resolved_today,

        'agent_customer_satisfaction_display': satisfaction_display,

        # Add URLs for template components to avoid circular references
        'header_url': '/dashboard/agent-dashboard/partials/header.html',
        'sidebar_url': '/dashboard/agent-dashboard/partials/sidebar.html',
        'modals_url': '/dashboard/agent-dashboard/partials/modals.html',

    }



    return render(request, 'agentdashboard/index.html', ctx)





@login_required

def agent_dashboard_page(request, page):

    """Serve sub-pages and partials for the Agent dashboard.

    This allows URLs like /dashboard/agent-dashboard/partials/header.html

    and /dashboard/agent-dashboard/tickets.html to work similarly to the

    admin and user dashboards.

    """

    # Check if user has agent privileges - STRICT ROLE CHECK
    if not is_agent_user(request):
        # Log the unauthorized access attempt
        role_name = getattr(request.user.userprofile.role, 'name', 'No profile') if hasattr(request.user, 'userprofile') and getattr(request.user.userprofile, 'role', None) else 'No profile'
        logger.warning(f"Unauthorized access attempt by {request.user.username} (role: {role_name}) to agent dashboard page: {page}")
        
        # Redirect appropriate dashboard based on user role
        if is_admin_user(request):
            return redirect('dashboards:admin_dashboard')
        elif is_regular_user(request):
            return redirect('dashboards:user_dashboard')
        else:
            return redirect('dashboards:user_dashboard')

    # Handle trailing slash issue - remove trailing slash if present
    if page.endswith('/'):
        page = page.rstrip('/')

    allowed_pages = {
        'tickets.html',
        'chat.html',
        'agenttickets.html',
        'reports.html',
        'ratings.html',
        'profile.html',
        'contact.html',
        'settings.html',
        'partials/header.html',
        'partials/sidebar.html',
        'partials/modals.html',
        'css/style.css',
        'tickets',
        'chat',
        'agenttickets',
        'reports',
        'ratings',
        'profile',
        'contact',
        'settings',
        'partials/header',
        'partials/sidebar',
        'partials/modals',
    }

    if page not in allowed_pages:

        # For safety, do not render arbitrary templates

        from django.http import Http404

        raise Http404("Page not found")



    # Ensure template name always has .html extension
    # Handle pages that might come without .html extension
    pages_needing_html = ['tickets', 'chat', 'agenttickets', 'reports', 'ratings', 'profile', 'contact', 'settings', 'partials/header', 'partials/sidebar', 'partials/modals']
    
    if page in pages_needing_html:
        template_name = f'agentdashboard/{page}.html'
    else:
        template_name = f'agentdashboard/{page}'

    ctx = {}


    # Agent tickets listing page: tickets "under" this agent (assigned to OR created by them)
    if page == 'tickets.html' or page == 'tickets':
        user = request.user
        tickets_qs = Ticket.objects.select_related('created_by').filter(
            Q(assigned_to=user) | Q(created_by=user)
        ).order_by('-created_at')
        ctx['agent_tickets'] = tickets_qs


    # Agent "My Tickets" page with summary stats

    if page == 'agenttickets.html' or page == 'agenttickets':

        user = request.user

        base_qs = Ticket.objects.select_related('created_by').filter(assigned_to=user)



        # Summary counts

        open_count = base_qs.filter(status='Open').count()

        pending_count = base_qs.filter(status='In Progress').count()



        seven_days_ago = timezone.now() - timezone.timedelta(days=7)

        resolved_7d_count = base_qs.filter(

            status__in=['Resolved', 'Closed'],

            updated_at__gte=seven_days_ago,

        ).count()



        breached_sla_count = base_qs.filter(

            status__in=['Open', 'In Progress'],

            priority__in=['High', 'Critical'],

        ).count()



        ctx.update({

            'agenttickets_open_count': open_count,

            'agenttickets_pending_count': pending_count,

            'agenttickets_resolved_7d_count': resolved_7d_count,

            'agenttickets_breached_sla_count': breached_sla_count,

            'agenttickets_list': base_qs.order_by('-created_at'),

        })



    # Agent ratings/performance page: show ratings data

    if page == 'ratings.html' or page == 'ratings':

        user = request.user



        # Show only ratings received by this agent, newest first.

        qs = UserRating.objects.select_related('user', 'agent').filter(agent=user).order_by('-created_at')

        total = qs.count()



        agg = qs.aggregate(

            avg_rating=Avg('rating'),

            c5=Count('id', filter=Q(rating=5)),

            c4=Count('id', filter=Q(rating=4)),

            c3=Count('id', filter=Q(rating=3)),

            c2=Count('id', filter=Q(rating=2)),

            c1=Count('id', filter=Q(rating=1)),

        ) if total else {"avg_rating": 0, "c5": 0, "c4": 0, "c3": 0, "c2": 0, "c1": 0}



        avg_val = float(agg.get('avg_rating') or 0.0)

        c5 = int(agg.get('c5') or 0)

        c4 = int(agg.get('c4') or 0)

        c3 = int(agg.get('c3') or 0)

        c2 = int(agg.get('c2') or 0)

        c1 = int(agg.get('c1') or 0)



        def pct(count):

            return int((count / total) * 100) if total else 0



        # Tickets assigned to this agent (used for response rate / time)

        agent_tickets = Ticket.objects.filter(assigned_to=user)

        total_tickets = agent_tickets.count()



        # Simple response-rate approximation: tickets not in pure "Open" state

        responded_tickets = agent_tickets.filter(status__in=['In Progress', 'Resolved', 'Closed']).count()

        agent_response_rate = int((responded_tickets / total_tickets) * 100) if total_tickets else 0



        # Satisfaction: percentage of 4★ and 5★ ratings

        positive_ratings = qs.filter(rating__gte=4).count()

        agent_satisfaction = int((positive_ratings / total) * 100) if total else 0



        # Average response / resolution time based on ticket timestamps

        avg_response_hours = 0.0

        if total_tickets:

            resolved_qs = agent_tickets.filter(status__in=['Resolved', 'Closed'])

            if resolved_qs.exists():

                duration_expr = ExpressionWrapper(F('updated_at') - F('created_at'), output_field=DurationField())

                dur_agg = resolved_qs.aggregate(avg_duration=Avg(duration_expr))

                avg_duration = dur_agg.get('avg_duration')

                if avg_duration is not None:

                    total_seconds = float(avg_duration.total_seconds())

                    avg_response_hours = round(total_seconds / 3600.0, 1)



        recent_activity = Ticket.objects.filter(assigned_to=user).order_by('-updated_at')[:5]



        ctx.update({

            # Original rating metrics

            'agent_ratings': qs,

            'agent_avg_rating': round(avg_val, 1),

            'agent_total_reviews': total,

            'agent_count_5': c5,

            'agent_count_4': c4,

            'agent_count_3': c3,

            'agent_count_2': c2,

            'agent_count_1': c1,

            'agent_percent_5': pct(c5),

            'agent_percent_4': pct(c4),

            'agent_percent_3': pct(c3),

            'agent_percent_2': pct(c2),

            'agent_percent_1': pct(c1),



            # New top-card metrics

            'agent_response_rate': agent_response_rate,

            'agent_satisfaction': agent_satisfaction,

            'agent_avg_response_hours': avg_response_hours,



            'agent_recent_activity': recent_activity,

        })



    # Agent reports/analytics page: ticket aggregates for this agent

    if page == 'reports.html' or page == 'reports':

        user = request.user

        base_qs = Ticket.objects.filter(assigned_to=user)



        total_tickets = base_qs.count()



        # Status distribution

        status_defaults = {"Open": 0, "In Progress": 0, "Resolved": 0, "Closed": 0}

        for row in base_qs.values('status').annotate(c=Count('id')):

            key = row['status']

            if key in status_defaults:

                status_defaults[key] = row['c']



        resolved_total = status_defaults["Resolved"] + status_defaults["Closed"]

        resolution_rate = int((resolved_total / total_tickets) * 100) if total_tickets else 0



        # Average response/resolution time (created_at -> updated_at)

        avg_response_display = "0h 0m"

        if total_tickets:

            resolved_qs = base_qs.filter(status__in=["Resolved", "Closed"])

            if resolved_qs.exists():

                duration_expr = ExpressionWrapper(F("updated_at") - F("created_at"), output_field=DurationField())

                agg = resolved_qs.aggregate(avg_duration=Avg(duration_expr))

                avg_duration = agg.get("avg_duration")

                if avg_duration is not None:

                    total_seconds = int(avg_duration.total_seconds())

                    hours = total_seconds // 3600

                    minutes = (total_seconds % 3600) // 60

                    avg_response_display = f"{hours}h {minutes}m"



        # Customer satisfaction from ratings for this agent

        ratings_qs = UserRating.objects.filter(agent=user)

        ratings_total = ratings_qs.count()

        csat_display = "0.0/5"

        if ratings_total:

            ratings_agg = ratings_qs.aggregate(avg_rating=Avg("rating"))

            avg_val = float(ratings_agg.get("avg_rating") or 0.0)

            csat_display = f"{round(avg_val, 1)}/5"



        # Status percentages for donut chart [Open, Resolved, In Progress]

        def pct(count):

            return int((count / total_tickets) * 100) if total_tickets else 0



        open_count = status_defaults["Open"]

        inprog_count = status_defaults["In Progress"]

        resolved_count = resolved_total



        open_percent = pct(open_count)

        inprog_percent = pct(inprog_count)

        resolved_percent = pct(resolved_count)



        status_percents = [open_percent, resolved_percent, inprog_percent]



        # Priority distribution [Low, Medium, High, Critical]

        priority_defaults = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}

        for row in base_qs.values('priority').annotate(c=Count('id')):

            key = row['priority']

            if key in priority_defaults:

                priority_defaults[key] = row['c']



        priority_counts = [

            priority_defaults["Low"],

            priority_defaults["Medium"],

            priority_defaults["High"],

            priority_defaults["Critical"],

        ]



        # Overview chart per month for current year

        now = timezone.now()

        current_year = now.year

        month_labels = []

        created_counts = []

        resolved_counts = []



        for month in range(1, 13):

            month_labels.append(calendar.month_abbr[month])



            created_qs = base_qs.filter(created_at__year=current_year, created_at__month=month)

            created_counts.append(created_qs.count())



            resolved_qs = base_qs.filter(

                updated_at__year=current_year,

                updated_at__month=month,

                status__in=['Resolved', 'Closed'],

            )

            resolved_counts.append(resolved_qs.count())

        # Display name for agent
        display_name = (user.get_full_name() or '').strip() or user.username

        # Calculate resolved_7d_count for reports
        seven_days_ago = timezone.now() - timezone.timedelta(days=7)
        resolved_7d_count = base_qs.filter(
            status__in=['Resolved', 'Closed'],
            updated_at__gte=seven_days_ago,
        ).count()

        # Calculate breached_sla_count for reports
        breached_sla_count = base_qs.filter(
            status__in=['Open', 'In Progress'],
            created_at__lt=timezone.now() - timezone.timedelta(hours=24)  # Assuming 24h SLA
        ).count()

        # Update context with reports data
        ctx.update({
            'agent_report_total_tickets': total_tickets,
            'agent_report_resolved_total': resolved_total,
            'agent_report_avg_response_display': avg_response_display,
            'agent_report_resolution_rate': resolution_rate,
            'agent_report_csat_display': csat_display,
            'agent_report_user_name': display_name,
            'agent_report_open_percent': open_percent,
            'agent_report_resolved_percent': resolved_percent,
            'agent_report_inprogress_percent': inprog_percent,
            'agent_report_resolved_7d_count': resolved_7d_count,
            'agent_report_breached_sla_count': breached_sla_count,
            'agent_report_status_percents_json': json.dumps(status_percents),
            'agent_report_priority_counts_json': json.dumps(priority_counts),
            'agent_report_overview_months_json': json.dumps(month_labels),
            'agent_report_overview_created_json': json.dumps(created_counts),
            'agent_report_overview_resolved_json': json.dumps(resolved_counts),
            # Channel data for reports
            'agent_report_channel_email_count': 15,
            'agent_report_channel_phone_count': 8,
            'agent_report_channel_chat_count': 12,
            'agent_report_channel_web_count': 5,
        })

    # Default values for reports context
    else:
        display_name = (request.user.get_full_name() or '').strip() or request.user.username
        avg_response_display = "0h 0m"
        resolution_rate = 0
        csat_display = "0.0/5"
        open_percent = 0
        resolved_7d_count = 0
        breached_sla_count = 0
        status_percents = [0, 0, 0]
        priority_counts = [0, 0, 0, 0]
        month_labels = []
        created_counts = []
        resolved_counts = []

    # Customer satisfaction for this agent's reports
    ratings_qs = UserRating.objects.filter(agent=request.user)
    satisfaction_display = "0.0/5"
    if ratings_qs.exists():
        ratings_agg = ratings_qs.aggregate(avg_rating=Avg('rating'))
        avg_val = float(ratings_agg.get('avg_rating') or 0.0)
        satisfaction_display = f"{round(avg_val, 1)}/5"

    # Add URLs for template components to avoid circular references
    ctx.update({
        'agent_customer_satisfaction_display': satisfaction_display,
        'header_url': '/dashboard/agent-dashboard/partials/header.html',
        'sidebar_url': '/dashboard/agent-dashboard/partials/sidebar.html',
        'modals_url': '/dashboard/agent-dashboard/partials/modals.html',
    })

    # Agent settings page: use shared SiteSettings for general/system configuration

    if page == 'settings.html' or page == 'settings':

        settings_obj = SiteSettings.get_solo()

        settings_saved = False

        # Always add settings to context for both GET and POST requests
        ctx.update({
            'agent_settings': settings_obj,
            'agent_settings_saved': settings_saved,
        })

        if request.method == "POST":

            company_name = (request.POST.get('company_name') or '').strip()

            website_url = (request.POST.get('website_url') or '').strip()

            contact_email = (request.POST.get('contact_email') or '').strip()

            contact_phone = (request.POST.get('contact_phone') or '').strip()

            address = (request.POST.get('address') or '').strip()



            default_language = (request.POST.get('default_language') or '').strip()

            time_zone = (request.POST.get('time_zone') or '').strip()

            date_format = (request.POST.get('date_format') or '').strip()

            time_format = (request.POST.get('time_format') or '').strip()

            first_day_of_week_val = request.POST.get('first_day_of_week')

            currency = (request.POST.get('currency') or '').strip()



            maintenance_mode = bool(request.POST.get('maintenance_mode'))

            user_registration = bool(request.POST.get('user_registration'))

            email_verification = bool(request.POST.get('email_verification'))

            remember_me = bool(request.POST.get('remember_me'))

            show_tutorial = bool(request.POST.get('show_tutorial'))



            # Handle company logo provided as a data URL in a hidden field

            company_logo_data = (request.POST.get('company_logo') or '').strip()

            if company_logo_data:

                # If it's a data URL (base64) -> decode and save

                if company_logo_data.startswith('data:image'):

                    try:

                        header, encoded = company_logo_data.split(',', 1)

                        data = base64.b64decode(encoded)

                        # Derive extension from header

                        ext = 'png'

                        if 'jpeg' in header or 'jpg' in header:

                            ext = 'jpg'

                        elif 'gif' in header:

                            ext = 'gif'

                        filename = f"site_logo_{uuid.uuid4().hex}.{ext}"

                        settings_obj.company_logo.save(filename, ContentFile(data), save=False)

                    except Exception:

                        # ignore decode errors and leave existing logo intact

                        pass

                else:

                    # If a URL or empty string provided, do nothing (URL will be handled client-side)

                    pass

            else:

                # If explicitly cleared (empty string), remove existing logo

                try:

                    if getattr(settings_obj, 'company_logo'):

                        settings_obj.company_logo.delete(save=False)

                except Exception:

                    pass



            if default_language:

                settings_obj.default_language = default_language

            if time_zone:

                settings_obj.time_zone = time_zone

            if date_format:

                settings_obj.date_format = date_format

            if time_format:

                settings_obj.time_format = time_format

            if currency:

                settings_obj.currency = currency



            try:

                if first_day_of_week_val is not None:

                    settings_obj.first_day_of_week = int(first_day_of_week_val)

            except (TypeError, ValueError):

                pass



            settings_obj.maintenance_mode = maintenance_mode

            settings_obj.user_registration = user_registration

            settings_obj.email_verification = email_verification

            settings_obj.remember_me = remember_me

            settings_obj.show_tutorial = show_tutorial

            # Collapsed logo toggle (checkbox)

            settings_obj.collapsed_logo = bool(request.POST.get('collapsed_logo'))

            # Handle reset defaults request

            if request.POST.get('reset_defaults'):

                # Reset all settings to default values

                settings_obj.company_name = 'TicketHub'

                settings_obj.website_url = 'https://tickethub.example.com'

                settings_obj.contact_email = 'support@tickethub.example.com'

                settings_obj.contact_phone = '+1 (555) 123-4567'

                settings_obj.address = '123 Main St, City, State 12345'

                settings_obj.default_language = 'English (United States)'

                settings_obj.time_zone = '(UTC-05:00) Eastern Time (US & Canada)'

                settings_obj.date_format = 'MM/DD/YYYY'

                settings_obj.time_format = '12-hour'

                settings_obj.first_day_of_week = 0

                settings_obj.maintenance_mode = False

                settings_obj.user_registration = True

                settings_obj.email_verification = True

                settings_obj.remember_me = True

                settings_obj.show_tutorial = True

                settings_obj.collapsed_logo = False

                # Clear logo if exists

                try:

                    if getattr(settings_obj, 'company_logo'):

                        settings_obj.company_logo.delete(save=False)

                except Exception:

                    pass

                settings_obj.save()

                settings_saved = True

            try:
                settings_obj.save()
                settings_saved = True
                
                # Return JSON response for AJAX requests
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': 'Settings saved successfully!',
                        'data': {
                            'company_name': settings_obj.company_name,
                            'website_url': settings_obj.website_url,
                            'contact_email': settings_obj.contact_email,
                            'contact_phone': settings_obj.contact_phone,
                            'address': settings_obj.address,
                            'default_language': settings_obj.default_language,
                            'time_zone': settings_obj.time_zone,
                            'date_format': settings_obj.date_format,
                            'time_format': settings_obj.time_format,
                            'currency': settings_obj.currency,
                            'maintenance_mode': settings_obj.maintenance_mode,
                            'user_registration': settings_obj.user_registration,
                            'email_verification': settings_obj.email_verification,
                            'remember_me': settings_obj.remember_me,
                            'show_tutorial': settings_obj.show_tutorial,
                            'collapsed_logo': settings_obj.collapsed_logo
                        }
                    })
                else:
                    # Regular form submission - redirect to prevent double submission
                    settings_saved = True

            except Exception:
                pass

    # Agent profile page: reuse user profile logic for the logged-in agent

    if page == 'profile.html' or page == 'profile':

        user = request.user

        profile = getattr(user, 'userprofile', None)

        if profile is None:

            profile = UserProfile.objects.create(user=user)



        full_name = (user.get_full_name() or '').strip()

        phone = getattr(profile, 'phone', '') if profile else ''

        role_obj = getattr(profile, 'role', None) if profile else None

        role_name = getattr(role_obj, 'name', '') or 'Agent'



        profile_saved = False

        password_saved = False

        password_error = ''



        if request.method == "POST":

            action = request.POST.get('action')

            if action == 'profile':

                new_full = (request.POST.get('fullName') or '').strip()

                new_email = (request.POST.get('email') or '').strip()

                new_phone = (request.POST.get('phone') or '').strip()

                new_department = (request.POST.get('department') or '').strip()

                new_address = (request.POST.get('address') or '').strip()



                # Handle optional profile picture upload

                picture_file = request.FILES.get('profile_picture')



                if new_full:

                    parts = new_full.split()

                    if len(parts) == 1:

                        user.first_name = parts[0]

                        user.last_name = ''

                    else:

                        user.first_name = ' '.join(parts[:-1])

                        user.last_name = parts[-1]

                if new_email:

                    user.email = new_email

                user.save()



                if profile:

                    profile.phone = new_phone

                    if new_department:

                        profile.department = new_department

                    if new_address:

                        profile.address = new_address

                    if picture_file:
                        print(f"DEBUG: Saving profile picture: {picture_file.name}")
                        profile.profile_picture = picture_file
                    else:
                        print("DEBUG: No picture_file to save")

                    profile.save()
                    print(f"DEBUG: Profile saved. Profile picture field: {profile.profile_picture}")
                    if profile.profile_picture:
                        print(f"DEBUG: Profile picture name after save: {profile.profile_picture.name}")
                    else:
                        print("DEBUG: Profile picture is None after save")

                    profile_saved = True



            elif action == 'remove_profile_picture':

                # Handle profile picture removal

                if profile and profile.profile_picture:

                    # Delete the file from storage
                    try:
                        import os
                        from django.conf import settings
                        if profile.profile_picture and hasattr(profile.profile_picture, 'path'):
                            file_path = profile.profile_picture.path
                            if os.path.exists(file_path):
                                os.remove(file_path)
                    except Exception:
                        pass  # Ignore file deletion errors
                    
                    # Clear the profile picture field
                    profile.profile_picture = None
                    profile.save()
                    profile_saved = True



            elif action == 'password':

                pw = request.POST.get('password') or ''

                cf = request.POST.get('confirm') or ''

                if not pw or pw != cf:

                    password_error = 'Passwords do not match.'

                else:

                    user.set_password(pw)

                    user.save()

                    update_session_auth_hash(request, user)

                    password_saved = True



            elif action == 'notifications':

                # Basic notification/preferences toggles stored on UserProfile

                email_notifications = bool(request.POST.get('email_notifications'))

                desktop_notifications = bool(request.POST.get('desktop_notifications'))

                show_activity_status = bool(request.POST.get('show_activity_status'))

                allow_dm_from_non_contacts = bool(request.POST.get('allow_dm_from_non_contacts'))



                profile.email_notifications = email_notifications

                profile.desktop_notifications = desktop_notifications

                profile.show_activity_status = show_activity_status

                profile.allow_dm_from_non_contacts = allow_dm_from_non_contacts

                profile.save()

        # Add profile context variables for the template
        ctx.update({
            'profile_user': user,
            'profile_obj': profile,
            'profile_full_name': full_name or user.username,
            'profile_email': user.email,
            'profile_phone': phone,
            'profile_role': role_name,
            'profile_saved': profile_saved,
            'password_saved': password_saved,
            'password_error': password_error,
            # Profile statistics
            'profile_tickets_closed': Ticket.objects.filter(assigned_to=user, status__in=['Resolved', 'Closed']).count(),
            'profile_avg_rating_display': f"{UserRating.objects.filter(agent=user).aggregate(avg=Avg('rating'))['avg'] or 0:.1f}/5",
            'profile_avg_first_response_display': '0m',  # Placeholder - can be calculated from actual data
            # Notification settings
            'notif_email': getattr(profile, 'email_notifications', True) if profile else True,
            'notif_desktop': getattr(profile, 'desktop_notifications', False) if profile else False,
            'notif_show_activity': getattr(profile, 'show_activity_status', True) if profile else True,
            'notif_allow_dm': getattr(profile, 'allow_dm_from_non_contacts', False) if profile else False,
        })

    # Add URLs for template components to avoid circular references
    ctx.update({
        'header_url': '/dashboard/agent-dashboard/partials/header.html',
        'sidebar_url': '/dashboard/agent-dashboard/partials/sidebar.html',
        'modals_url': '/dashboard/agent-dashboard/partials/modals.html',
    })

    # Chat page logic
    if page == 'chat.html' or page == 'chat':
        user = request.user
        
        # Find a support admin for the user to chat with
        support_admin = (
            User.objects.filter(is_staff=True, is_active=True)
            .order_by('id')
            .first()
        )
        
        # Get user's ticket IDs
        user_ticket_ids = list(
            Ticket.objects
            .filter(created_by=request.user)
            .order_by('-created_at')
            .values_list('ticket_id', flat=True)
        )
        
        # Update context with chat variables
        ctx.update({
            'support_admin': support_admin,
            'chat_ticket_ids': user_ticket_ids,
            'chat_ticket_id': user_ticket_ids[0] if user_ticket_ids else '',
            'chat_user': user,
            'chat_messages': [],  # Will be populated from ChatMessage model
        })

    return render(request, template_name, ctx)


@login_required

def user_dashboard(request):
    
    # ROLE VALIDATION: Only allow regular users to access user dashboard
    if is_admin_user(request) or is_agent_user(request):
        # Redirect admins to admin dashboard and agents to agent dashboard
        if is_admin_user(request):
            return redirect("dashboards:admin_dashboard")
        elif is_agent_user(request):
            return redirect("dashboards:agent_dashboard")
    
    if not is_regular_user(request):
        # If user doesn't have a valid role, redirect to login
        return redirect("users:login")


    # IMPORTANT FIX: Handle payment completion flag first to prevent modal showing after payment

    payment_completed = request.session.get('payment_completed', False)

    payment_completed_user_id = request.session.get('payment_completed_user_id')
    
    if payment_completed and payment_completed_user_id == request.user.id:

        # Clear any modal flags that might have been set before payment completion

        if 'show_payment_modal' in request.session:

            del request.session['show_payment_modal']

        if 'expiry_info' in request.session:

            del request.session['expiry_info']

        request.session.modified = True

    

    # Build dynamic context for the user dashboard

    all_qs = Ticket.objects.select_related('created_by').filter(created_by=request.user).order_by('-created_at')



    # Optional status filter via query param

    status_filter = request.GET.get('status')

    valid_statuses = {"Open", "In Progress", "Resolved", "Closed"}

    qs = all_qs

    if status_filter in valid_statuses:

        qs = all_qs.filter(status=status_filter)



    total = all_qs.count()



    # Simple, explicit counts so badges always match the list filters

    open_count = all_qs.filter(status='Open').count()

    in_progress_count = all_qs.filter(status='In Progress').count()

    resolved_count = all_qs.filter(status='Resolved').count()



    # Compute user display info

    full_name = (request.user.get_full_name() or '').strip()

    if full_name:

        parts = [p for p in full_name.split() if p]

        user_initials = ''.join([p[0].upper() for p in parts[:2]])

        user_display_name = full_name

    else:

        uname = request.user.username or ''

        user_initials = (uname[:2] or 'U').upper()

        user_display_name = uname or 'User'



    ctx = {

        'tickets': qs,

        'total_tickets': total,

        'open_count': open_count,

        'in_progress_count': in_progress_count,

        'resolved_count': resolved_count,

        'user_initials': user_initials,

        'user_display_name': user_display_name,

        'current_status': status_filter or 'All',

    }



    # -----------------------------

    # PAYMENT MODAL LOGIC FOR USERS ONLY

    # -----------------------------

    # Check if payment modal should be shown for normal users only

    show_payment_modal = False

    plan_name = None

    expiry_date = None

    days_expired = 0

    

    

    # First check if modal was set from session (by middleware)

    if request.session.get('show_payment_modal', False):

        show_payment_modal = True

        expiry_info = request.session.get('expiry_info', {})

        plan_name = expiry_info.get('plan_name')

        expiry_date = expiry_info.get('expiry_date')

        days_expired = expiry_info.get('days_expired', 0)

    else:

        # Check user's subscription expiry using the comprehensive logic

        payment_completed = request.session.get('payment_completed', False)

        

        if not payment_completed:

            # Import the comprehensive check function

            from superadmin.views import should_show_payment_modal, get_user_plan_name, get_expiry_date, get_days_expired

            modal_should_show = should_show_payment_modal(request.user)

            

            if modal_should_show:

                show_payment_modal = True

                plan_name = get_user_plan_name(request.user)

                expiry_date = get_expiry_date(request.user)

                days_expired = get_days_expired(request.user)

            else:

                pass

        else:

            pass

    

    

    # FINAL SAFETY CHECK: If payment was completed, force modal to not show

    if request.session.get('payment_completed', False):

        show_payment_modal = False

    

    # Add payment modal context
    ctx.update({
        'show_payment_modal': show_payment_modal,
        'plan_name': plan_name,
        'expiry_date': expiry_date,
        'days_expired': days_expired,
    })

    return render(request, 'userdashboard/index.html', ctx)



@login_required

def dashboard_home(request):

    # Use strict role validation functions instead of loose checks
    if is_admin_user(request):
        return redirect("dashboards:admin_dashboard")
    elif is_agent_user(request):
        return redirect("dashboards:agent_dashboard")
    elif is_regular_user(request):
        return redirect("dashboards:user_dashboard")
    else:
        # If user doesn't have a valid role, redirect to login
        return redirect("users:login")







@ensure_csrf_cookie

def ticket_dashboard_page(request, page: str):

    # Handle trailing slash issue - remove trailing slash if present
    if page.endswith('/'):
        page = page.rstrip('/')

    allowed_pages = {

        'index.html', 'tickets.html', 'users.html', 'agents.html', 'customers.html',

        'roles.html', 'ratings.html', 'reports.html', 'custom-fields.html',

        'settings.html', 'chat.html'

    }

    if page not in allowed_pages:

        raise Http404("Page not found")

    base = "ticketdashboard 2 (2)/ticketdashboard 2/ticketdashboard/"

    return render(request, f"{base}{page}")





@login_required

def user_dashboard_page(request, page: str):

    # IMPORTANT FIX: Handle payment completion flag first to prevent modal showing after payment

    payment_completed = request.session.get('payment_completed', False)
    payment_completed_user_id = request.session.get('payment_completed_user_id')
    
    if payment_completed and payment_completed_user_id == request.user.id:

        # Clear any modal flags that might have been set before payment completion

        if 'show_payment_modal' in request.session:

            del request.session['show_payment_modal']

        if 'expiry_info' in request.session:

            del request.session['expiry_info']

        request.session.modified = True

    # Handle trailing slash issue - remove trailing slash if present
    if page.endswith('/'):
        page = page.rstrip('/')

    # Handle undefined page parameter

    if page == 'undefined' or not page:

        return redirect('dashboards:user_dashboard')

    

    # Convert incoming URL name -> correct template filename

    # Handle tickets explicitly to avoid any mapping issues

    if page == 'tickets':

        template_file = 'tickets.html'

    else:

        page_map = {

            'profile': 'profile.html',

            'settings': 'settings.html',

            'ticket': 'ticket.html',

            'chat': 'chat.html',

            'ratings': 'ratings.html',

            'faq': 'faq.html',

            'notifications': 'notifications.html',

        }



        # If user entered `/chat/` → convert to `chat.html`

        template_file = page_map.get(page)

        if not template_file:

            raise Http404("Page not found")



    base = "userdashboard/"

    ctx = {}



    # Compute user display info for header/avatar

    full_name = (request.user.get_full_name() or '').strip()

    if full_name:

        parts = [p for p in full_name.split() if p]

        user_initials = ''.join([p[0].upper() for p in parts[:2]])

        user_display_name = full_name

    else:

        uname = request.user.username or ''

        user_initials = (uname[:2] or 'U').upper()

        user_display_name = uname or 'User'



    # Ticket counters for sidebar (used on all user pages)

    user_tickets_qs = Ticket.objects.select_related('created_by').filter(created_by=request.user)

    total_tickets = user_tickets_qs.count()



    # Explicit counts to keep sidebar badges in sync with dashboard filters

    open_count = user_tickets_qs.filter(status='Open').count()

    in_progress_count = user_tickets_qs.filter(status='In Progress').count()

    resolved_count = user_tickets_qs.filter(status='Resolved').count()



    ctx.update({

        'user_initials': user_initials,

        'user_display_name': user_display_name,

        'total_tickets': total_tickets,

        'open_count': open_count,

        'in_progress_count': in_progress_count,

        'resolved_count': resolved_count,

        # On sub-pages we treat the current filter as "All" for sidebar highlighting

        'current_status': 'All',

    })



    # If this is the tickets sub-page, expose the full ticket list for this user

    if template_file == 'tickets.html':

        tickets_list = list(user_tickets_qs.select_related('assigned_to').order_by('-created_at'))

        ctx['tickets'] = tickets_list



        ticket_ids = [t.ticket_id for t in tickets_list]

        ratings_qs = (

            UserRating.objects

            .filter(user=request.user, ticket_reference__in=ticket_ids)

            .order_by('-created_at')

        )

        ratings_map = {r.ticket_reference: r for r in ratings_qs}

        for t in tickets_list:

            setattr(t, 'user_rating', ratings_map.get(getattr(t, 'ticket_id', '')))



    # -----------------------------

    # CHAT PAGE

    # -----------------------------

    if template_file == 'chat.html':

        support_admin = (

            User.objects.filter(is_staff=True, is_active=True)

            .order_by('id')

            .first()

        )

        ctx['support_admin'] = support_admin



        user_ticket_ids = list(

            Ticket.objects

            .filter(created_by=request.user)

            .order_by('-created_at')

            .values_list('ticket_id', flat=True)

        )

        ctx['chat_ticket_ids'] = user_ticket_ids

        ctx['chat_ticket_id'] = user_ticket_ids[0] if user_ticket_ids else ''



    # -----------------------------

    # PROFILE PAGE

    # -----------------------------

    if template_file == 'profile.html':

        user = request.user

        profile = getattr(user, 'userprofile', None)



        # Fresh values

        full_name = (user.get_full_name() or '').strip()

        phone = getattr(profile, 'phone', '') if profile else ''

        role_obj = getattr(profile, 'role', None) if profile else None

        role_name = getattr(role_obj, 'name', '') or 'User'



        profile_saved = False

        password_saved = False

        password_error = ''



        if request.method == "POST":

            action = request.POST.get('action')

            if action == 'profile':

                new_full = (request.POST.get('fullName') or '').strip()

                new_email = (request.POST.get('email') or '').strip()

                new_phone = (request.POST.get('phone') or '').strip()

                new_address = (request.POST.get('address') or '').strip()

                new_date_of_birth = request.POST.get('date_of_birth')

                new_gender = (request.POST.get('gender') or '').strip()

                # Handle optional profile picture upload
                picture_file = request.FILES.get('profile_picture')
                
                # Debug: Log file upload information
                print(f"DEBUG: Profile picture upload - picture_file: {picture_file}")
                if picture_file:
                    print(f"DEBUG: File name: {picture_file.name}")
                    print(f"DEBUG: File size: {picture_file.size}")
                    print(f"DEBUG: File content type: {picture_file.content_type}")
                else:
                    print("DEBUG: No profile picture file found in request.FILES")
                    print(f"DEBUG: request.FILES keys: {list(request.FILES.keys())}")
                    print(f"DEBUG: request.POST keys: {list(request.POST.keys())}")

                if new_full:

                    parts = new_full.split()

                    if len(parts) == 1:

                        user.first_name = parts[0]

                        user.last_name = ''

                    else:

                        user.first_name = ' '.join(parts[:-1])

                        user.last_name = parts[-1]



                if new_email:

                    user.email = new_email

                user.save()



                # Update profile if it exists

                if profile:

                    profile.phone = new_phone

                    if new_address:

                        profile.address = new_address

                    if new_date_of_birth:

                        from datetime import datetime

                        try:

                            profile.date_of_birth = datetime.strptime(new_date_of_birth, '%Y-%m-%d').date()

                        except ValueError:

                            pass  # Invalid date format, ignore

                    if new_gender:

                        profile.gender = new_gender

                    if picture_file:

                        profile.profile_picture = picture_file

                    profile.save()

                else:

                    # Create profile if it doesn't exist
                    profile = UserProfile.objects.create(user=user, phone=new_phone)

                    if new_address:

                        profile.address = new_address

                    if new_date_of_birth:

                        from datetime import datetime

                        try:

                            profile.date_of_birth = datetime.strptime(new_date_of_birth, '%Y-%m-%d').date()

                        except ValueError:

                            pass

                    if new_gender:

                        profile.gender = new_gender

                    if picture_file:

                        profile.profile_picture = picture_file

                    profile.save()



                profile_saved = True



                full_name = (user.get_full_name() or '').strip()

                phone = getattr(profile, 'phone', '') if profile else ''



            elif action == 'remove_profile_picture':

                # Handle profile picture removal

                if profile and profile.profile_picture:

                    # Delete the file from storage
                    try:
                        import os
                        from django.conf import settings
                        if profile.profile_picture and hasattr(profile.profile_picture, 'path'):
                            file_path = profile.profile_picture.path
                            if os.path.exists(file_path):
                                os.remove(file_path)
                    except Exception:
                        pass  # Ignore file deletion errors
                    
                    # Clear the profile picture field
                    profile.profile_picture = None
                    profile.save()
                    profile_saved = True



            elif action == 'password':

                pw = request.POST.get('password') or ''

                cf = request.POST.get('confirm') or ''

                if not pw or pw != cf:

                    password_error = 'Passwords do not match.'

                else:

                    user.set_password(pw)

                    user.save()

                    update_session_auth_hash(request, user)

                    password_saved = True



        ctx.update({

            'profile_user': user,

            'profile_obj': profile,

            'profile_full_name': full_name or user.username,

            'profile_email': user.email,

            'profile_phone': phone,

            'profile_role': role_name,

            'profile_saved': profile_saved,

            'password_saved': password_saved,

            'password_error': password_error,

        })



    # -----------------------------

    # SETTINGS PAGE

    # -----------------------------

    if template_file == 'settings.html':

        user = request.user

        profile = getattr(user, 'userprofile', None)

        if profile is None:

            profile = UserProfile.objects.create(user=user)



        settings_saved = False

        password_changed = False

        password_error = ''

        twofa_changed = False

        twofa_error = ''



        if request.method == "POST":

            action = request.POST.get('action') or 'settings'



            # Main settings card (theme + notification toggles)

            if action == 'settings':

                theme_value = (request.POST.get('theme') or profile.theme or 'system').strip()

                profile.theme = theme_value

                profile.dark_mode = (theme_value == 'dark')



                profile.email_notifications = bool(request.POST.get('email_notifications'))

                profile.desktop_notifications = bool(request.POST.get('push_notifications'))

                profile.allow_dm_from_non_contacts = bool(request.POST.get('marketing_emails'))



                profile.save()

                settings_saved = True



            # Change password

            elif action == 'change_password':

                current_password = request.POST.get('current_password', '').strip()

                new_password = request.POST.get('new_password', '').strip()

                confirm_password = request.POST.get('confirm_password', '').strip()



                if not user.check_password(current_password):

                    password_error = 'Current password is incorrect.'

                elif new_password != confirm_password:

                    password_error = 'New passwords do not match.'

                elif len(new_password) < 8:

                    password_error = 'Password must be at least 8 characters long.'

                elif not any(c.isupper() for c in new_password):

                    password_error = 'Password must contain at least one uppercase letter.'

                elif not any(c.isdigit() for c in new_password):

                    password_error = 'Password must contain at least one number.'

                else:

                    try:

                        user.set_password(new_password)

                        user.save()

                        password_changed = True

                        # Also set user session key to None to log them out after password change

                        messages.success(request, 'Password changed successfully. Please login again.')

                        return redirect('dashboards:user_dashboard_page', page='settings')

                    except Exception as e:

                        password_error = str(e)



            # Toggle 2FA

            elif action == 'toggle_2fa':

                if getattr(profile, 'two_factor_enabled', False):

                    # Disable 2FA

                    confirm_password = request.POST.get('confirm_password', '').strip()

                    if not user.check_password(confirm_password):

                        twofa_error = 'Password is incorrect. 2FA was not disabled.'

                    else:

                        profile.two_factor_enabled = False

                        profile.save()

                        twofa_changed = True

                        messages.success(request, 'Two-factor authentication has been disabled.')

                else:

                    # Enable 2FA

                    verification_code = request.POST.get('verification_code', '').strip()

                    if len(verification_code) != 6 or not verification_code.isdigit():

                        twofa_error = 'Please enter a valid 6-digit verification code.'

                    else:

                        # In a real implementation, you would verify the code against the TOTP secret

                        # For now, we'll just enable it

                        profile.two_factor_enabled = True

                        profile.save()

                        twofa_changed = True

                        messages.success(request, 'Two-factor authentication has been enabled.')



            # Danger zone: deactivate account (soft deactivate)

            elif action == 'deactivate':

                profile.is_active = False

                user.is_active = False

                profile.save()

                user.save()

                # Log the user out by redirecting to logout view

                return redirect('users:logout')



            # Danger zone: delete account (soft delete -> mark inactive)

            elif action == 'delete':

                profile.is_active = False

                user.is_active = False

                profile.save()

                user.save()

                return redirect('users:logout')



        ctx.update({

            'settings_dark_mode': profile.dark_mode,

            'settings_theme': profile.theme,

            'settings_email_notifications': profile.email_notifications,

            'settings_desktop_notifications': profile.desktop_notifications,

            'settings_show_activity_status': profile.show_activity_status,

            'settings_allow_dm_from_non_contacts': profile.allow_dm_from_non_contacts,

            'settings_push_notifications': profile.desktop_notifications,

            'settings_marketing_emails': profile.allow_dm_from_non_contacts,

            'settings_2fa_enabled': getattr(profile, 'two_factor_enabled', False),

            'settings_account_active': profile.is_active,

            'settings_saved': settings_saved,

            'password_changed': password_changed,

            'password_error': password_error,

            'twofa_changed': twofa_changed,

            'twofa_error': twofa_error,

        })



    # -----------------------------

    # RATINGS PAGE

    # -----------------------------

    if template_file == 'ratings.html':

        user = request.user

        

        # User's tickets for associating a review

        user_tickets = (

            Ticket.objects

            .filter(created_by=user)

            .order_by('-created_at')

        )



        rating_saved = False

        rating_error = ''



        if request.method == 'POST':

            # Parse and validate form inputs

            rating_str = (request.POST.get('overall_rating') or request.POST.get('rating') or '').strip()

            title = (request.POST.get('title') or '').strip()

            content = (request.POST.get('content') or '').strip()

            recommend_val = (request.POST.get('recommend') or '').strip().lower()

            ticket_ref_str = (request.POST.get('ticket') or '').strip()



            try:

                rating_val = int(float(rating_str)) if rating_str else 0

            except ValueError:

                rating_val = 0



            recommend_bool = True if recommend_val == 'yes' else False if recommend_val == 'no' else None



            # Basic validation

            if rating_val < 1 or rating_val > 5:

                rating_error = 'Please select a valid rating between 1 and 5.'

            elif not title:

                rating_error = 'Please provide a review title.'

            elif not content:

                rating_error = 'Please provide your review content.'

            elif recommend_bool is None:

                rating_error = 'Please select whether you recommend our service.'

            else:

                # Resolve selected ticket (optional)

                selected_ticket = None

                agent = None

                ticket_reference = None

                if ticket_ref_str:

                    selected_ticket = Ticket.objects.filter(ticket_id=ticket_ref_str, created_by=user).first()

                    if selected_ticket:

                        agent = selected_ticket.assigned_to

                        ticket_reference = selected_ticket.ticket_id

                

                # Create the rating entry

                try:

                    UserRating.objects.create(

                        user=user,

                        agent=agent,

                        ticket_reference=ticket_reference,

                        rating=rating_val,

                        title=title,

                        content=content,

                        recommend=bool(recommend_bool),

                    )

                    rating_saved = True

                    # Post/Redirect/Get to avoid duplicate submissions

                    return redirect('/dashboard/user-dashboard/ratings')

                except Exception:

                    rating_error = 'An error occurred while saving your review. Please try again.'



        # Aggregate user's own ratings

        ratings_qs = (

            UserRating.objects

            .select_related('user')

            .filter(user=user)

            .order_by('-created_at')

        )

        total_reviews = ratings_qs.count()

        agg = ratings_qs.aggregate(

            avg_rating=Avg('rating'),

            c5=Count('id', filter=Q(rating=5)),

            c4=Count('id', filter=Q(rating=4)),

            c3=Count('id', filter=Q(rating=3)),

            c2=Count('id', filter=Q(rating=2)),

            c1=Count('id', filter=Q(rating=1)),

        ) if total_reviews else {

            'avg_rating': 0.0, 'c5': 0, 'c4': 0, 'c3': 0, 'c2': 0, 'c1': 0,

        }



        avg_val = float(agg.get('avg_rating') or 0.0)

        c5 = int(agg.get('c5') or 0)

        c4 = int(agg.get('c4') or 0)

        c3 = int(agg.get('c3') or 0)

        c2 = int(agg.get('c2') or 0)

        c1 = int(agg.get('c1') or 0)



        def pct(x: int) -> int:

            return int((x / total_reviews) * 100) if total_reviews else 0



        ctx.update({

            'avg_rating': round(avg_val, 1),

            'total_reviews': total_reviews,

            'count_5': c5,

            'count_4': c4,

            'count_3': c3,

            'count_2': c2,

            'count_1': c1,

            'percent_5': pct(c5),

            'percent_4': pct(c4),

            'percent_3': pct(c3),

            'percent_2': pct(c2),

            'percent_1': pct(c1),

            'user_tickets': user_tickets,

            'ratings': ratings_qs,

            'rating_saved': rating_saved,

            'rating_error': rating_error,

        })



    # -----------------------------

    # FAQ PAGE

    # -----------------------------

    if template_file == 'faq.html':

        # Structured FAQ data. You can later move this to a model.

        faq_sections = [

            {

                'key': 'getting-started',

                'title': 'Getting Started',

                'description': 'Basics of using the TicketHub portal as an end user.',

                'items': [

                    {

                        'question': 'How do I create a new ticket?',

                        'answer': 'Go to the dashboard sidebar and click the "New Ticket" button. Fill in the subject, category, description and optional attachments, then submit.'

                    },

                    {

                        'question': 'How can I see all my tickets?',

                        'answer': 'Open the Tickets section in the left menu or use the Dashboard counters (Open, In Progress, Resolved) to filter your tickets.'

                    },

                    {

                        'question': 'What information should I include in a ticket?',

                        'answer': 'Include a clear title, detailed description of the issue, error messages if any, steps to reproduce, and screenshots where possible.'

                    },

                ],

            },

            {

                'key': 'tickets',

                'title': 'Tickets & Statuses',

                'description': 'Learn what each ticket status means and how updates work.',

                'items': [

                    {

                        'question': 'What do the ticket statuses mean?',

                        'answer': '"Open" means your request is received, "In Progress" means an agent is working on it, "Resolved" means a solution was provided, and "Closed" is finalised after confirmation.'

                    },

                    {

                        'question': 'Can I reopen a resolved ticket?',

                        'answer': 'If the issue is not fully solved, you can reply in the ticket conversation or create a new ticket referencing the old one.'

                    },

                    {

                        'question': 'How long does it take to get a response?',

                        'answer': 'Response time depends on priority, but high and critical tickets are usually handled first. You can see SLA information in your ticket details if configured by the admin.'

                    },

                ],

            },

            {

                'key': 'billing',

                'title': 'Billing & Payments',

                'description': 'Questions about invoices, subscriptions and payments.',

                'items': [

                    {

                        'question': 'How do I update my billing information?',

                        'answer': 'Open the Billing or Settings section (if enabled by your organisation) and update your payment method and billing address.'

                    },

                    {

                        'question': 'Where can I download my invoices?',

                        'answer': 'Invoices are usually available under your Billing or Account section. If you cannot find them, create a billing ticket and our team will help.'

                    },

                ],

            },

            {

                'key': 'account',

                'title': 'Account & Profile',

                'description': 'Manage your profile, password and notifications.',

                'items': [

                    {

                        'question': 'How do I change my password?',

                        'answer': 'Go to the Profile page in your user dashboard, open the Security or Password section, and follow the steps to change your password.'

                    },

                    {

                        'question': 'Can I update my email or phone number?',

                        'answer': 'Yes. On the Profile page you can update your contact information. Some fields may be locked depending on your organisation settings.'

                    },

                    {

                        'question': 'How do notification settings work?',

                        'answer': 'In Settings you can enable or disable email and desktop notifications for ticket updates, chat replies and system announcements.'

                    },

                ],

            },

            {

                'key': 'troubleshooting',

                'title': 'Troubleshooting',

                'description': 'Fix common issues when using the portal.',

                'items': [

                    {

                        'question': 'I am not receiving email notifications.',

                        'answer': 'First check your spam folder. Then verify your email address in the Profile page and confirm that email notifications are enabled in Settings.'

                    },

                    {

                        'question': 'The page is not loading correctly.',

                        'answer': 'Try refreshing the page, clearing your browser cache, or using a different browser. If the problem continues, create a technical ticket.'

                    },

                ],

            },

        ]



        # Simple featured list (first few FAQs from any section)

        featured_faqs = []

        for section in faq_sections:

            for item in section['items']:

                if len(featured_faqs) < 3:

                    featured_faqs.append({

                        'question': item['question'],

                        'answer': item['answer'],

                        'category': section['title'],

                    })

                else:

                    break

            if len(featured_faqs) >= 3:

                break



        ctx.update({

            'faq_sections': faq_sections,

            'featured_faqs': featured_faqs,

        })



    # -----------------------------

    # NOTIFICATIONS PAGE

    # -----------------------------

    if template_file == 'notifications.html':

        user = request.user



        # Collect recent notifications from tickets and chat messages

        notifications = []



        # Ticket-based notifications (created_by = current user)

        ticket_qs = (

            Ticket.objects

            .filter(created_by=user)

            .order_by('-updated_at')[:20]

        )

        for t in ticket_qs:

            notifications.append({

                'timestamp': t.updated_at,

                'category': 'tickets',

                'icon': 'fas fa-ticket-alt',

                'is_unread': t.status in ['Open', 'In Progress'],

                'text': f"Ticket #{t.ticket_id} · {t.title} · status: {t.status}",

                'actions': [

                    {

                        'label': 'View Ticket',

                        'url': f"/dashboard/user-dashboard/ticket/{t.ticket_id}/",

                    },

                ],

            })



        # Chat-based notifications (messages sent to current user)

        chat_qs = (

            ChatMessage.objects

            .select_related('sender')

            .filter(recipient=user)

            .order_by('-created_at')[:20]

        )

        for m in chat_qs:

            notifications.append({

                'timestamp': m.created_at,

                'category': 'system',

                'icon': 'fas fa-comment',

                'is_unread': not m.is_read,

                'text': f"New message from {m.sender.get_full_name() or m.sender.username}",

                'actions': [

                    {

                        'label': 'Open Chat',

                        'url': '/dashboard/user-dashboard/chat/',

                    },

                ],

            })



        # Sort all notifications by most recent

        notifications.sort(key=lambda n: n['timestamp'], reverse=True)



        # Group into Today / Yesterday / Older

        today = timezone.now().date()

        yesterday = today - timezone.timedelta(days=1)

        groups = {

            'Today': [],

            'Yesterday': [],

            'Older': [],

        }

        for n in notifications:

            d = n['timestamp'].date()

            if d == today:

                groups['Today'].append(n)

            elif d == yesterday:

                groups['Yesterday'].append(n)

            else:

                groups['Older'].append(n)



        notifications_groups = [

            {'label': label, 'items': items}

            for label, items in groups.items()

            if items

        ]



        ctx.update({

            'notifications_groups': notifications_groups,

        })



    # -----------------------------

    # PAYMENT MODAL LOGIC FOR USERS ONLY

    # -----------------------------

    # Check if payment modal should be shown for normal users only

    show_payment_modal = False

    plan_name = None

    expiry_date = None

    days_expired = 0

    

    

    # First check if modal was set from session (by middleware)

    if request.session.get('show_payment_modal', False):

        show_payment_modal = True

        expiry_info = request.session.get('expiry_info', {})

        plan_name = expiry_info.get('plan_name')

        expiry_date = expiry_info.get('expiry_date')

        days_expired = expiry_info.get('days_expired', 0)

    else:

        # Check user's subscription expiry using the comprehensive logic

        payment_completed = request.session.get('payment_completed', False)

        

        if not payment_completed:

            # Import the comprehensive check function

            from superadmin.views import should_show_payment_modal, get_user_plan_name, get_expiry_date, get_days_expired

            modal_should_show = should_show_payment_modal(request.user)

            

            if modal_should_show:

                show_payment_modal = True

                plan_name = get_user_plan_name(request.user)

                expiry_date = get_expiry_date(request.user)

                days_expired = get_days_expired(request.user)

            else:

                pass

        else:

            pass

    

    

    # FINAL SAFETY CHECK: If payment was completed, force modal to not show

    if request.session.get('payment_completed', False):

        show_payment_modal = False

    

    # Add payment modal context

    ctx.update({

        'show_payment_modal': show_payment_modal,

        'plan_name': plan_name,

        'expiry_date': expiry_date,

        'days_expired': days_expired,

    })



    # -----------------------------
    
    # TICKET CREATION PAGE
    # -----------------------------
    
    if template_file == 'ticket.html':
        # Handle POST request for ticket creation
        if request.method == 'POST':
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                from tickets.models import TicketAttachment
                
                form = TicketForm(request.POST, request.FILES)
                if form.is_valid():
                    ticket = form.save(commit=False)
                    if ticket.category == "Others":
                        other_value = request.POST.get("category_other", "").strip()
                        if other_value:
                            ticket.category = other_value
                    ticket.created_by = request.user
                    ticket.save()

                    # Handle file attachments
                    files = request.FILES.getlist('attachments')
                    for f in files:
                        TicketAttachment.objects.create(ticket=ticket, file=f)

                    return JsonResponse({
                        'success': True,
                        'message': 'Ticket created successfully!',
                        'ticket_id': ticket.id
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'error': 'Form validation failed. Please check all required fields.',
                        'errors': form.errors
                    })
            else:
                print("DEBUG: Non-AJAX POST request - ignoring")
                # Handle non-AJAX POST normally (redirect to tickets/create)
                pass

    # -----------------------------
    
    # SETTINGS PAGE
    # -----------------------------
    
    if template_file == 'settings.html':
        # Initialize variables
        profile_saved = False
        password_saved = False
        
        try:
            # Get or create user profile
            user_profile, created = UserProfile.objects.get_or_create(user=request.user)
            
            # Handle POST request for settings
            if request.method == 'POST':
                action = request.POST.get('action')
                
                if action == 'settings':
                    # Update user preferences
                    user_profile.dark_mode = request.POST.get('theme') == 'dark'
                    user_profile.theme = request.POST.get('theme', 'light')
                    user_profile.email_notifications = request.POST.get('email_notifications') == 'on'
                    user_profile.desktop_notifications = request.POST.get('push_notifications') == 'on'
                    user_profile.save()
                    
                    messages.success(request, 'Settings saved successfully!')
                    return redirect('dashboards:user_dashboard_page', page='settings')
                
                elif action == 'change_password':
                    # Handle password change
                    current_password = request.POST.get('current_password')
                    new_password = request.POST.get('new_password')
                    confirm_password = request.POST.get('confirm_password')
                    
                    if request.user.check_password(current_password):
                        if new_password == confirm_password:
                            request.user.set_password(new_password)
                            request.user.save()
                            messages.success(request, 'Password changed successfully. Please login again.')
                            return redirect('users:logout')
                        else:
                            messages.error(request, 'New passwords do not match.')
                    else:
                        messages.error(request, 'Current password is incorrect.')
                
                elif action == 'toggle_2fa':
                    # Handle 2FA toggle (placeholder)
                    messages.info(request, '2FA feature coming soon!')
                
                elif action == 'deactivate':
                    # Handle account deactivation (placeholder)
                    messages.info(request, 'Account deactivation feature coming soon!')
                
                elif action == 'delete':
                    # Handle account deletion (placeholder)
                    messages.error(request, 'Account deletion feature coming soon!')
            
            # Add settings context
            ctx.update({
                'settings_dark_mode': user_profile.dark_mode,
                'settings_theme': user_profile.theme,
                'settings_email_notifications': user_profile.email_notifications,
                'settings_push_notifications': user_profile.desktop_notifications,
                'settings_2fa_enabled': False,  # Placeholder
                'profile_saved': profile_saved,
                'password_saved': password_saved,
            })
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            messages.error(request, f'Error loading settings: {e}')



    # Check if this is an AJAX request (for profile save)

    if request.method == "POST" and request.headers.get('X-Requested-With') == 'XMLHttpRequest':

        return JsonResponse({

            'success': True,

            'profile_saved': profile_saved,

            'password_saved': password_saved,

            'password_error': password_error,

        })



    # FINAL RENDER

    return render(request, f"{base}{template_file}", ctx)





@csrf_exempt

@login_required

def clear_payment_modal(request):

    """Clear payment modal flags from session"""

    if request.method == 'POST':

        try:

            # Clear session flags

            if 'show_payment_modal' in request.session:

                del request.session['show_payment_modal']

            if 'expiry_info' in request.session:

                del request.session['expiry_info']

            request.session['payment_completed'] = True
            request.session['payment_completed_user_id'] = request.user.id

            request.session.modified = True

            

            return JsonResponse({'success': True})

        except Exception as e:

            return JsonResponse({'success': False, 'error': str(e)})

    

    return JsonResponse({'success': False, 'error': 'Method not allowed'})





@csrf_exempt

@login_required

def record_payment_transaction(request):

    """Record payment transaction in database"""

    if request.method == 'POST':

        try:

            import json

            data = json.loads(request.body)

            

            plan_name = data.get('plan_name', 'Unknown Plan')

            amount = data.get('amount', '199')

            payment_method = data.get('payment_method', 'Credit Card')

            

            

            # Import the Payment model and related models

            from superadmin.models import Payment, Company, Subscription, Plan

            

            # Get or create company for the user

            company_name = f'{request.user.username} Company'

            company, created = Company.objects.get_or_create(

                name=company_name,

                defaults={

                    'email': request.user.email,

                    'phone': '',

                    'address': ''

                }

            )

            

            # Get or create a plan (use Basic plan as default)

            plan, created = Plan.objects.get_or_create(

                name='Basic',

                defaults={

                    'price': float(amount),

                    'billing_cycle': 'monthly',

                    'users': 1,

                    'storage': '10GB',

                    'status': 'active'

                }

            )

            

            # Get or create subscription for the company

            subscription, created = Subscription.objects.get_or_create(

                company=company,

                plan=plan,

                defaults={

                    'start_date': timezone.now().date(),

                    'end_date': timezone.now().date() + timezone.timedelta(days=30),

                    'status': 'active',

                    'billing_cycle': 'monthly',

                    'amount': float(amount)

                }

            )

            

            # If subscription already exists, update it

            if not created:

                subscription.start_date = timezone.now().date()

                subscription.end_date = timezone.now().date() + timezone.timedelta(days=30)

                subscription.status = 'active'

                subscription.billing_cycle = 'monthly'

                subscription.amount = float(amount)

                subscription.save()

            

            

            # Create payment record

            payment = Payment.objects.create(

                subscription=subscription,

                company=company,

                amount=float(amount),

                payment_method=payment_method.lower().replace(' ', '_'),

                payment_type='subscription',

                status='completed',

                transaction_id=f'TXN{int(timezone.now().timestamp())}',

                payment_date=timezone.now()

            )

            

            

            # Verify the payment was created

            try:

                verify_payment = Payment.objects.get(id=payment.id)

            except Exception as e:

                pass

            

            return JsonResponse({'success': True, 'transaction_id': payment.transaction_id})

        except Exception as e:

            import traceback

            traceback.print_exc()

            return JsonResponse({'success': False, 'error': str(e)})

    

    return JsonResponse({'success': False, 'error': 'Method not allowed'})





def _parse_report_date_range(request):

    label = (request.GET.get('date_range') or '').strip().lower()

    start_raw = (request.GET.get('start_date') or '').strip()

    end_raw = (request.GET.get('end_date') or '').strip()



    now = timezone.now()

    today = now.date()



    def _parse_date(val):

        try:

            return datetime.date.fromisoformat(val)

        except Exception:

            return None



    if label in {'last 7 days', '7', 'last7'}:

        start = today - datetime.timedelta(days=6)

        end = today

        return start, end

    if label in {'last 30 days', '30', 'last30'}:

        start = today - datetime.timedelta(days=29)

        end = today

        return start, end

    if label in {'this month', 'month'}:

        start = today.replace(day=1)

        end = today

        return start, end

    if label in {'last month'}:

        first_this_month = today.replace(day=1)

        last_month_end = first_this_month - datetime.timedelta(days=1)

        start = last_month_end.replace(day=1)

        end = last_month_end

        return start, end

    if label in {'this year', 'year'}:

        start = today.replace(month=1, day=1)

        end = today

        return start, end



    start = _parse_date(start_raw)

    end = _parse_date(end_raw)

    if start and end:

        if end < start:

            start, end = end, start

        return start, end



    return None, None





def _simple_pdf_bytes(lines, title='Report'):

    text = [title] + [''] + (lines or [])

    y_start = 800

    y_step = 14

    content_lines = [

        'BT',

        '/F1 12 Tf',

        f'72 {y_start} Td',

    ]

    for i, line in enumerate(text):

        safe = (line or '').replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')

        if i == 0:

            content_lines.append(f'({safe}) Tj')

        else:

            content_lines.append(f'0 -{y_step} Td')

            content_lines.append(f'({safe}) Tj')

    content_lines.append('ET')

    content_stream = ('\n'.join(content_lines) + '\n').encode('latin-1', errors='replace')



    objects = []

    objects.append(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")

    objects.append(b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n")

    objects.append(b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n")

    objects.append(b"4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n")

    objects.append(b"5 0 obj\n<< /Length %d >>\nstream\n" % len(content_stream) + content_stream + b"endstream\nendobj\n")



    header = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"

    xref_positions = [0]

    body = io.BytesIO()

    body.write(header)

    for obj in objects:

        xref_positions.append(body.tell())

        body.write(obj)

    xref_start = body.tell()

    body.write(b"xref\n0 %d\n" % (len(objects) + 1))

    body.write(b"0000000000 65535 f \n")

    for pos in xref_positions[1:]:

        body.write(f"{pos:010d} 00000 n \n".encode('ascii'))

    body.write(

        b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objects) + 1, xref_start)

    )

    return body.getvalue()





@login_required

def admin_reports_export(request, export_format: str):

    user = request.user

    is_admin = bool(

        user.is_authenticated and (

            user.is_superuser or user.is_staff or (

                hasattr(user, 'userprofile')

                and getattr(getattr(user.userprofile, 'role', None), 'name', '').lower() == 'admin'

            )

        )

    )

    if not is_admin:

        return HttpResponseForbidden('Forbidden')



    export_format = (export_format or '').strip().lower()

    report_type = (request.GET.get('report_type') or 'ticket_summary').strip().lower()



    start, end = _parse_report_date_range(request)

    tickets = Ticket.objects.select_related('created_by', 'assigned_to').all().order_by('-created_at')

    if start and end:

        start_dt = timezone.make_aware(datetime.datetime.combine(start, datetime.time.min))

        end_dt = timezone.make_aware(datetime.datetime.combine(end, datetime.time.max))

        tickets = tickets.filter(created_at__range=(start_dt, end_dt))



    if report_type in {'ticket_summary', 'tickets'}:

        if export_format == 'csv':

            output = io.StringIO()

            writer = csv.writer(output)

            writer.writerow(['Ticket ID', 'Title', 'Status', 'Priority', 'Created At', 'Updated At', 'Created By', 'Assigned To'])

            for t in tickets:

                created_by = getattr(getattr(t, 'created_by', None), 'username', '')

                assigned_to = getattr(getattr(t, 'assigned_to', None), 'username', '')

                writer.writerow([

                    getattr(t, 'ticket_id', ''),

                    getattr(t, 'title', ''),

                    getattr(t, 'status', ''),

                    getattr(t, 'priority', ''),

                    timezone.localtime(getattr(t, 'created_at')).strftime('%Y-%m-%d %H:%M') if getattr(t, 'created_at', None) else '',

                    timezone.localtime(getattr(t, 'updated_at')).strftime('%Y-%m-%d %H:%M') if getattr(t, 'updated_at', None) else '',

                    created_by,

                    assigned_to,

                ])



            resp = HttpResponse(output.getvalue(), content_type='text/csv; charset=utf-8')

            resp['Content-Disposition'] = 'attachment; filename="ticket_summary.csv"'

            return resp



        if export_format == 'pdf':

            lines = []

            for t in tickets[:200]:

                lines.append(

                    f"#{getattr(t, 'ticket_id', '')} | {getattr(t, 'status', '')} | {getattr(t, 'priority', '')} | {getattr(t, 'title', '')}"

                )

            pdf_bytes = _simple_pdf_bytes(lines, title='Ticket Summary')

            resp = HttpResponse(pdf_bytes, content_type='application/pdf')

            resp['Content-Disposition'] = 'attachment; filename="ticket_summary.pdf"'

            return resp



    if report_type in {'agent_performance', 'agents'}:

        agent_qs = (

            User.objects

            .select_related('userprofile', 'userprofile__role')

            .filter(userprofile__role__name='Agent')

            .annotate(

                assigned_count=Count('assigned_tickets', distinct=True),

                resolved_count=Count(

                    'assigned_tickets',

                    filter=Q(assigned_tickets__status__in=['Resolved', 'Closed']),

                    distinct=True,

                ),

            )

            .order_by('username')

        )



        rows = []

        for u in agent_qs:

            assigned = getattr(u, 'assigned_count', 0) or 0

            resolved = getattr(u, 'resolved_count', 0) or 0

            perf = int((resolved / assigned) * 100) if assigned else 0

            rows.append({

                'name': (u.get_full_name() or '').strip() or u.username,

                'email': u.email,

                'assigned': assigned,

                'resolved': resolved,

                'performance_percent': perf,

            })



        if export_format == 'csv':

            output = io.StringIO()

            writer = csv.writer(output)

            writer.writerow(['Agent', 'Email', 'Assigned', 'Resolved', 'Performance %'])

            for r in rows:

                writer.writerow([r['name'], r['email'], r['assigned'], r['resolved'], r['performance_percent']])

            resp = HttpResponse(output.getvalue(), content_type='text/csv; charset=utf-8')

            resp['Content-Disposition'] = 'attachment; filename="agent_performance.csv"'

            return resp



        if export_format == 'pdf':

            lines = [f"{r['name']} ({r['email']}) | assigned: {r['assigned']} | resolved: {r['resolved']} | perf: {r['performance_percent']}%" for r in rows]

            pdf_bytes = _simple_pdf_bytes(lines, title='Agent Performance')

            resp = HttpResponse(pdf_bytes, content_type='application/pdf')

            resp['Content-Disposition'] = 'attachment; filename="agent_performance.pdf"'

            return resp



    if report_type in {'custom'}:

        metric = (request.GET.get('metric') or 'status').strip().lower()

        if metric not in {'status', 'priority'}:

            metric = 'status'



        values = (

            tickets.values(metric)

            .annotate(count=Count('id'))

            .order_by('-count')

        )



        if export_format == 'csv':

            output = io.StringIO()

            writer = csv.writer(output)

            writer.writerow([metric.title(), 'Count'])

            for row in values:

                writer.writerow([row.get(metric) or '', row.get('count') or 0])

            resp = HttpResponse(output.getvalue(), content_type='text/csv; charset=utf-8')

            resp['Content-Disposition'] = 'attachment; filename="custom_report.csv"'

            return resp



        if export_format == 'pdf':

            lines = [f"{row.get(metric) or ''}: {row.get('count') or 0}" for row in values]

            pdf_bytes = _simple_pdf_bytes(lines, title=f'Custom Report ({metric})')

            resp = HttpResponse(pdf_bytes, content_type='application/pdf')

            resp['Content-Disposition'] = 'attachment; filename="custom_report.pdf"'

            return resp



    raise Http404('Unsupported export')





@login_required

@ensure_csrf_cookie

def admin_dashboard_page(request, page: str):

    # Check if user has admin privileges - STRICT ROLE CHECK
    if not is_admin_user(request):
        # Log the unauthorized access attempt
        role_name = getattr(request.user.userprofile.role, 'name', 'No profile') if hasattr(request.user, 'userprofile') and getattr(request.user.userprofile, 'role', None) else 'No profile'
        logger.warning(f"Unauthorized access attempt by {request.user.username} (role: {role_name}) to admin dashboard page: {page}")
        
        # Redirect appropriate dashboard based on user role
        if is_agent_user(request):
            return redirect('dashboards:agent_dashboard')
        elif is_regular_user(request):
            return redirect('dashboards:user_dashboard')
        else:
            return redirect('dashboards:user_dashboard')

    allowed_pages = {

        'index.html', 'tickets.html', 'users.html', 'agents.html', 'customers.html',

        'roles.html', 'ratings.html', 'reports.html', 'custom-fields.html',

        'settings.html', 'chat.html', 'profile.html',

        # partials used by the dashboard

        'partials/header.html', 'partials/sidebar.html', 'partials/modals.html'

    }

    # Normalize: strip trailing slashes and allow extensionless paths

    raw = page.strip('/')

    # If a nested path was sent (e.g. 'tickets.html/partials/modals.html'),

    # collapse to the partials segment if present; otherwise take the basename

    parts = raw.split('/') if raw else []

    if 'partials' in parts:

        idx = parts.index('partials')

        normalized = '/'.join(parts[idx:])

    else:

        normalized = parts[-1] if parts else raw

    if not normalized.endswith('.html'):

        normalized = f"{normalized}.html"

    if normalized not in allowed_pages:

        raise Http404("Page not found")

    base = "admindashboard/"

    # When rendering tickets.html, also provide a server-side queryset as initial data

    ctx = {}

    if normalized == 'tickets.html':

        if request.user.is_authenticated and (

            request.user.is_superuser or request.user.is_staff or (

                hasattr(request.user, "userprofile") and getattr(request.user.userprofile.role, "name", "").lower() == "admin"

            )

        ):

            qs = Ticket.objects.select_related('created_by').order_by('-created_at')

        else:

            qs = Ticket.objects.select_related('created_by').filter(created_by=request.user).order_by('-created_at')

        ctx = {"tickets": qs}

    elif normalized == 'profile.html':

        user = request.user

        profile = getattr(user, 'userprofile', None)

        if profile is None:

            profile = UserProfile.objects.create(user=user)



        profile_saved = False

        password_saved = False

        password_error = ''



        if request.method == 'POST':

            action = (request.POST.get('action') or '').strip()

            # Fallback: if action missing but password fields posted, treat as password change

            if not action and (

                request.POST.get('current_password') is not None

                or request.POST.get('new_password') is not None

                or request.POST.get('confirm_password') is not None

            ):

                action = 'password'



            if action == 'profile':

                new_full = (request.POST.get('full_name') or '').strip()

                new_email = (request.POST.get('email') or '').strip()

                new_phone = (request.POST.get('phone') or '').strip()

                new_city = (request.POST.get('city') or '').strip()

                new_state = (request.POST.get('state') or '').strip()

                new_country = (request.POST.get('country') or '').strip()

                new_address = (request.POST.get('address') or '').strip()

                picture_file = request.FILES.get('profile_picture')



                if new_full:

                    parts = [p for p in new_full.split() if p]

                    if len(parts) == 1:

                        user.first_name = parts[0]

                        user.last_name = ''

                    else:

                        user.first_name = ' '.join(parts[:-1])

                        user.last_name = parts[-1]



                if new_email:

                    user.email = new_email



                user.save()



                # Update profile if it exists
                if profile:

                    profile.phone = new_phone

                    if new_city:

                        profile.city = new_city

                    if new_state:

                        profile.state = new_state

                    if new_country:

                        profile.country = new_country

                    if new_address:

                        profile.address = new_address

                    if picture_file:

                        profile.profile_picture = picture_file

                    profile.save()

                else:

                    # Create profile if it doesn't exist
                    profile = UserProfile.objects.create(user=user, phone=new_phone)

                    if new_city:

                        profile.city = new_city

                    if new_state:

                        profile.state = new_state

                    if new_country:

                        profile.country = new_country

                    if new_address:

                        profile.address = new_address

                    if picture_file:

                        profile.profile_picture = picture_file

                    profile.save()

                profile_saved = True



            elif action == 'remove_profile_picture':

                # Handle profile picture removal

                if profile and profile.profile_picture:

                    # Delete the file from storage
                    try:
                        import os
                        from django.conf import settings
                        if profile.profile_picture and hasattr(profile.profile_picture, 'path'):
                            file_path = profile.profile_picture.path
                            if os.path.exists(file_path):
                                os.remove(file_path)
                    except Exception:
                        pass  # Ignore file deletion errors
                    
                    # Clear the profile picture field
                    profile.profile_picture = None
                    profile.save()
                    profile_saved = True



            elif action == 'password':

                current_password = request.POST.get('current_password') or ''

                new_password = request.POST.get('new_password') or ''

                confirm_password = request.POST.get('confirm_password') or ''



                if not current_password or not user.check_password(current_password):

                    password_error = 'Current password is incorrect.'

                elif not new_password:

                    password_error = 'New password is required.'

                elif new_password != confirm_password:

                    password_error = 'Passwords do not match.'

                else:

                    user.set_password(new_password)

                    user.save()

                    update_session_auth_hash(request, user)

                    password_saved = True



        ctx = {

            'profile_user': user,

            'profile_obj': profile,

            'profile_full_name': (user.get_full_name() or '').strip() or user.username,

            'profile_email': user.email,

            'profile_phone': getattr(profile, 'phone', '') or '',

            'profile_role': getattr(getattr(profile, 'role', None), 'name', '') or 'Admin',

            'profile_saved': profile_saved,

            'password_saved': password_saved,

            'password_error': password_error,

        }

    elif normalized == 'reports.html':

        # Basic ticket aggregates for the reports page

        qs = Ticket.objects.all()

        total_tickets = qs.count()



        status_defaults = {"Open": 0, "In Progress": 0, "Resolved": 0, "Closed": 0}

        for row in Ticket.objects.values('status').annotate(c=Count('id')):

            key = row['status']

            if key in status_defaults:

                status_defaults[key] = row['c']



        priority_defaults = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}

        for row in Ticket.objects.values('priority').annotate(c=Count('id')):

            key = row['priority']

            if key in priority_defaults:

                priority_defaults[key] = row['c']



        resolved_total = status_defaults["Resolved"] + status_defaults["Closed"]

        resolution_rate = int((resolved_total / total_tickets) * 100) if total_tickets else 0



        # Average resolution/response time across resolved/closed tickets

        avg_response_display = "0h 0m"

        if total_tickets:

            resolved_qs = qs.filter(status__in=["Resolved", "Closed"])

            if resolved_qs.exists():

                duration_expr = ExpressionWrapper(F("updated_at") - F("created_at"), output_field=DurationField())

                agg = resolved_qs.aggregate(avg_duration=Avg(duration_expr))

                avg_duration = agg.get("avg_duration")

                if avg_duration is not None:

                    total_seconds = int(avg_duration.total_seconds())

                    hours = total_seconds // 3600

                    minutes = (total_seconds % 3600) // 60

                    avg_response_display = f"{hours}h {minutes}m"



        # Overall customer satisfaction from all UserRating entries

        ratings_qs = UserRating.objects.all()

        ratings_total = ratings_qs.count()

        satisfaction_avg = 0.0

        satisfaction_percent = 0

        if ratings_total:

            ratings_agg = ratings_qs.aggregate(

                avg_rating=Avg("rating"),

                recommend_yes=Count("id", filter=Q(recommend=True)),

            )

            satisfaction_avg = float(ratings_agg.get("avg_rating") or 0.0)

            recommend_yes = int(ratings_agg.get("recommend_yes") or 0)

            satisfaction_percent = int((recommend_yes / ratings_total) * 100) if ratings_total else 0



        # Per-agent rating performance list for Agent Performance table

        # Include all agents (role 'Agent'), even if they have no ratings yet.

        agent_ratings_qs = (

            User.objects

            .select_related('userprofile', 'userprofile__role')

            .filter(userprofile__role__name='Agent')

            .annotate(

                avg_rating=Avg('received_ratings__rating'),

                rating_count=Count('received_ratings', distinct=True),

            )

            .order_by('username')

        )



        ratings_agent_perf = []

        for u in agent_ratings_qs:

            name = (u.get_full_name() or '').strip() or u.username

            initials = (name or '?')[:2].upper()

            avg_val = getattr(u, 'avg_rating', None)

            if avg_val is not None:

                avg_val = round(float(avg_val), 1)

            else:

                avg_val = 0.0

            ratings_agent_perf.append({

                "name": name,

                "initials": initials,

                "email": u.email,

                "avg_rating": avg_val,

                "rating_count": getattr(u, 'rating_count', 0) or 0,

            })



        # Build current year's 12 calendar months for overview chart (Jan–Dec)

        now = timezone.now()

        current_year = now.year

        month_labels = []

        created_counts = []

        resolved_counts = []



        for month in range(1, 13):

            month_labels.append(calendar.month_abbr[month])



            created_qs = qs.filter(created_at__year=current_year, created_at__month=month)

            created_counts.append(created_qs.count())



            resolved_qs = qs.filter(updated_at__year=current_year, updated_at__month=month, status__in=['Resolved', 'Closed'])

            resolved_counts.append(resolved_qs.count())



        # Agent performance aggregates: align with AgentsListView (role 'Agent')

        agent_qs = (

            User.objects

            .select_related('userprofile', 'userprofile__role')

            .filter(userprofile__role__name='Agent')

            .annotate(

                assigned_count=Count('assigned_tickets', distinct=True),

                resolved_count=Count(

                    'assigned_tickets',

                    filter=Q(assigned_tickets__status__in=["Resolved", "Closed"]),

                    distinct=True,

                ),

            )

            .order_by('username')

        )



        agent_perf = []

        for u in agent_qs:

            name = (u.get_full_name() or '').strip() or u.username

            initials = (name or '?')[:2].upper()

            assigned = getattr(u, 'assigned_count', 0) or 0

            resolved = getattr(u, 'resolved_count', 0) or 0

            perf = int((resolved / assigned) * 100) if assigned else 0

            agent_perf.append({

                "name": name,

                "initials": initials,

                "assigned": assigned,

                "resolved": resolved,

                "avg_response": "-",

                "avg_resolution": "-",

                "satisfaction": "-",

                "performance_percent": perf,

            })



        ctx = {

            "report_total_tickets": total_tickets,

            "report_resolution_rate": resolution_rate,

            "report_avg_response_display": avg_response_display,

            "report_customer_satisfaction_avg": round(satisfaction_avg, 1) if ratings_total else 0.0,

            "report_customer_satisfaction_percent": satisfaction_percent,

            "report_status_counts_json": json.dumps(status_defaults),

            "report_priority_counts_json": json.dumps(priority_defaults),

            "report_overview_months_json": json.dumps(month_labels),

            "report_overview_created_json": json.dumps(created_counts),

            "report_overview_resolved_json": json.dumps(resolved_counts),

            "report_agent_perf": agent_perf,

            "ratings_agent_perf": ratings_agent_perf,

        }

    elif normalized == 'ratings.html':

        # Overall ratings across all users for the admin Ratings page

        qs = UserRating.objects.select_related('user', 'agent').order_by('-created_at')

        total = qs.count()

        agg = qs.aggregate(

            avg_rating=Avg('rating'),

            c5=Count('id', filter=Q(rating=5)),

            c4=Count('id', filter=Q(rating=4)),

            c3=Count('id', filter=Q(rating=3)),

            c2=Count('id', filter=Q(rating=2)),

            c1=Count('id', filter=Q(rating=1)),

            recommend_yes=Count('id', filter=Q(recommend=True)),

        ) if total else {

            "avg_rating": 0,

            "c5": 0,

            "c4": 0,

            "c3": 0,

            "c2": 0,

            "c1": 0,

            "recommend_yes": 0,

        }



        avg_val = float(agg.get('avg_rating') or 0.0)

        c5 = int(agg.get('c5') or 0)

        c4 = int(agg.get('c4') or 0)

        c3 = int(agg.get('c3') or 0)

        c2 = int(agg.get('c2') or 0)

        c1 = int(agg.get('c1') or 0)

        recommend_yes = int(agg.get('recommend_yes') or 0)



        def pct(count):

            return int((count / total) * 100) if total else 0



        # Build per-agent performance from received ratings

        agent_qs = (

            User.objects

            .select_related('userprofile', 'userprofile__role')

            .filter(userprofile__role__name='Agent')

            .annotate(

                avg_rating=Avg('received_ratings__rating'),

                rating_count=Count('received_ratings', distinct=True),

            )

            .order_by('username')

        )



        ratings_agent_perf = []

        for u in agent_qs:

            name = (u.get_full_name() or '').strip() or u.username

            initials = (name or '?')[:2].upper()

            ratings_agent_perf.append({

                "name": name,

                "initials": initials,

                "email": u.email,

                "avg_rating": round(getattr(u, 'avg_rating', 0) or 0, 1),

                "rating_count": getattr(u, 'rating_count', 0) or 0,

            })



        ctx = {

            "ratings_admin_total": total,

            "ratings_admin_avg": round(avg_val, 1),

            "ratings_admin_count_5": c5,

            "ratings_admin_count_4": c4,

            "ratings_admin_count_3": c3,

            "ratings_admin_count_2": c2,

            "ratings_admin_count_1": c1,

            "ratings_admin_percent_5": pct(c5),

            "ratings_admin_percent_4": pct(c4),

            "ratings_admin_percent_3": pct(c3),

            "ratings_admin_percent_2": pct(c2),

            "ratings_admin_percent_1": pct(c1),

            # Satisfaction approximated as recommend == True

            "ratings_admin_satisfaction_percent": pct(recommend_yes),

            # Recent feedback list

            "ratings_admin_recent": qs[:20],

            # Per-agent rating performance

            "ratings_agent_perf": ratings_agent_perf,

        }

    elif normalized == 'users.html':

        # Build list of all users for the admin Users page

        user_qs = User.objects.select_related('userprofile', 'userprofile__role').order_by('username')

        users_list = []

        for u in user_qs:

            profile = getattr(u, 'userprofile', None)

            role_obj = getattr(profile, 'role', None) if profile else None

            role_name = getattr(role_obj, 'name', '') or ('Admin' if u.is_staff else 'User')



            # Map role to display label and badge class similar to roles.html

            if role_name == 'Admin':

                role_label = 'Administrator'

                role_badge_class = 'bg-primary'

            elif role_name == 'Agent':

                role_label = 'Agent'

                role_badge_class = 'bg-secondary'

            else:

                role_label = 'Customer'

                role_badge_class = 'bg-info'



            department = getattr(profile, 'department', '') if profile else ''

            is_active = getattr(profile, 'is_active', True) if profile is not None else u.is_active

            status_label = 'Active' if is_active else 'Inactive'

            status_badge_class = 'bg-success' if is_active else 'bg-secondary'



            full_name = (u.get_full_name() or '').strip() or u.username

            initials = (full_name or '?')[:2].upper()



            last_login = u.last_login

            if last_login:

                last_login_display = last_login.strftime('%d %b %Y, %I:%M %p')

            else:

                last_login_display = 'Never'



            users_list.append({

                'id': u.id,

                'name': full_name,

                'email': u.email,

                'role_name': role_name,

                'role_label': role_label,

                'role_badge_class': role_badge_class,

                'department': department or '-',

                'last_login_display': last_login_display,

                'status_label': status_label,

                'status_badge_class': status_badge_class,

                'initials': initials,

            })



        ctx = {

            'users_list': users_list,

            'users_total': len(users_list),

        }

    elif normalized == 'chat.html':

        # Build contacts from real users/userprofiles, but only customers (role 'User')

        user_qs = User.objects.select_related('userprofile').filter(

            is_staff=False,

            is_superuser=False,

        ).order_by('username')

        contacts = []

        for u in user_qs:

            full_name = (u.get_full_name() or '').strip() or u.username

            initials = ''

            if u.first_name or u.last_name:

                initials = (u.first_name[:1] + u.last_name[:1]).upper()

            else:

                initials = (u.username[:2]).upper()



            profile = getattr(u, 'userprofile', None)

            phone = getattr(profile, 'phone', '') if profile else ''

            location = getattr(profile, 'department', '') if profile else ''



            latest_chat_ticket_id = (

                ChatMessage.objects.filter(

                    Q(sender=u, recipient__is_staff=True) | Q(recipient=u, sender__is_staff=True)

                )

                .exclude(ticket_id__isnull=True)

                .exclude(ticket_id='')

                .order_by('-created_at')

                .values_list('ticket_id', flat=True)

                .first()

            )



            latest_ticket_id = (

                Ticket.objects

                .filter(created_by=u)

                .order_by('-created_at')

                .values_list('ticket_id', flat=True)

                .first()

            )



            active_ticket_id = latest_chat_ticket_id or latest_ticket_id or ""



            # Do not show customers that have no ticket thread to chat on.

            if not active_ticket_id:

                continue



            contacts.append({

                "id": u.id,

                "name": full_name,

                "initials": initials,

                "status": "Online" if u.is_active else "Offline",

                "last_message": "",  # can be filled from latest ChatMessage later

                "time": "",           # can be filled from timestamp later

                "unread_count": 0,     # can be computed from unread messages later

                "latest_ticket_id": active_ticket_id,

                "email": u.email,

                "phone": phone,

                "location": location,

                "member_since": u.date_joined.strftime('%b %Y') if u.date_joined else '',

                "total_tickets": f"{Ticket.objects.filter(created_by=u).count()} tickets",

                "last_active": "",    # can be set from last login or message later

            })



        active_contact = contacts[0] if contacts else None



        # For now, demo messages; later tie this to a ChatMessage model filtered by active_contact

        messages = []

        if active_contact:

            messages = [

                {

                    "direction": "received",

                    "text": f"Hello {{ active_contact.name }}! How can I help you today?",

                    "time": "10:30 AM",

                },

            ]



        ctx = {

            "contacts": contacts,

            "active_contact": active_contact,

            "messages": messages,

        }

    elif normalized == 'customers.html':

        # Build list of customers (users with 'User' role or non-staff users)
        
        customers_qs = (
            User.objects
            .select_related('userprofile', 'userprofile__role')
            .filter(
                Q(is_staff=False, is_superuser=False) |
                Q(userprofile__role__name='User')
            )
            .distinct()
            .annotate(tickets_count=Count('created_tickets', distinct=True))
            .order_by('-date_joined')
        )
        
        customers_list = []
        for user in customers_qs:
            profile = getattr(user, 'userprofile', None)
            role_obj = getattr(profile, 'role', None) if profile else None
            
            # Get initials
            full_name = (user.get_full_name() or '').strip() or user.username
            initials = (full_name or '?')[:2].upper()
            
            customers_list.append({
                'id': user.id,
                'name': full_name,
                'email': user.email,
                'username': user.username,
                'phone': getattr(profile, 'phone', '') or '',
                'department': getattr(profile, 'department', '') or '',
                'is_active': getattr(profile, 'is_active', True) if profile is not None else user.is_active,
                'is_vip': False,  # Could be added to profile model later
                'tickets_count': getattr(user, 'tickets_count', 0),
                'initials': initials,
                'date_joined': user.date_joined,
                'last_login': user.last_login,
                'role': getattr(role_obj, 'name', '') or 'User',
            })
        
        ctx = {
            'customers_list': customers_list,
            'customers_total': len(customers_list),
        }
    
    elif normalized == 'settings.html':
        # Load SiteSettings for the admin settings page
        settings_obj = SiteSettings.get_solo()
        ctx = {
            'site_settings': settings_obj,
        }
    
    return render(request, f"{base}{normalized}", ctx)





@login_required

def admin_ticket_detail(request, identifier: str):

    # Check if user has admin privileges - STRICT ROLE CHECK
    if not is_admin_user(request):
        # Log the unauthorized access attempt
        role_name = getattr(request.user.userprofile.role, 'name', 'No profile') if hasattr(request.user, 'userprofile') and getattr(request.user.userprofile, 'role', None) else 'No profile'
        logger.warning(f"Unauthorized access attempt by {request.user.username} (role: {role_name}) to admin ticket detail: {identifier}")
        
        # Return 404 for unauthorized access instead of redirect
        raise Http404("Not authorized")



    # Accept numeric pk (e.g., '42') or ticket_id variants (e.g., '#1204','1204','TCK-1204','#TCK-1204')

    ticket = None

    # 1) Try as numeric PK (after stripping leading '#')

    num = identifier.lstrip('#')

    if num.isdigit():

        ticket = Ticket.objects.filter(pk=int(num)).first()

    # 2) Try common ticket_id variants

    if ticket is None:

        candidates = []

        base = num

        if base:

            candidates.extend([base, f"TCK-{base}", f"#TCK-{base}"])

        raw = identifier

        if raw:

            candidates.extend([raw.lstrip('#'), raw, f"TCK-{raw.lstrip('#')}"])

        for cid in candidates:

            t = Ticket.objects.filter(ticket_id=cid).first()

            if t:

                ticket = t

                break

    if ticket is None:

        raise Http404("Ticket not found")



    # If this is an AJAX request from the user dashboard modal,

    # return a slim partial without the Bootstrap modal wrapper.

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':

        return render(

            request,

            'userdashboard/partials/ticket-detail-inner.html',

            {"ticket": ticket}

        )



    # Fallback: reuse the admin/agent modal partial if someone

    # visits the URL directly in a browser tab.

    return render(

        request,

        'admindashboard/partials/ticket-detail.html',

        {"ticket": ticket}

    )





@login_required

def user_ticket_delete(request, identifier: str):

    """Allow an end-user to delete their own ticket from the user dashboard."""

    user = request.user

    ticket = None



    num = identifier.lstrip('#')

    if num.isdigit():

        ticket = Ticket.objects.filter(pk=int(num)).first()



    if ticket is None:

        candidates = []

        base = num

        if base:

            candidates.extend([base, f"TCK-{base}", f"#TCK-{base}"])

        raw = identifier

        if raw:

            candidates.extend([raw.lstrip('#'), raw, f"TCK-{raw.lstrip('#')}"])

        for cid in candidates:

            t = Ticket.objects.filter(ticket_id=cid).first()

            if t:

                ticket = t

                break



    if ticket is None:

        raise Http404("Ticket not found")



    if ticket.created_by != user and not (user.is_staff or user.is_superuser):

        raise Http404("Not authorized")



    if request.method == "POST":

        ticket.delete()

    # Regardless of method, send the user back to their tickets list
    return redirect('dashboards:user_dashboard_page', page='tickets')


@login_required
def user_ticket_edit(request, identifier: str):
    """Allow an end-user to edit their own ticket from the user dashboard.
    Only allows editing for tickets with status 'Open' or 'In Progress'.
    """
    user = request.user
    
    # Resolve identifier to a Ticket instance (numeric pk or ticket_id variants)
    ticket = None
    num = identifier.lstrip('#')
    
    if num.isdigit():
        ticket = Ticket.objects.filter(pk=int(num)).first()
    
    if ticket is None:
        candidates = []
        base = num
        if base:
            candidates.extend([base, f"TCK-{base}", f"#TCK-{base}"])
        raw = identifier
        if raw:
            candidates.extend([raw.lstrip('#'), raw, f"TCK-{raw.lstrip('#')}"])
        
        for cid in candidates:
            t = Ticket.objects.filter(ticket_id=cid).first()
            if t:
                ticket = t
                break
    
    if ticket is None:
        raise Http404("Ticket not found")
    
    # Check if user owns this ticket
    if ticket.created_by != user:
        raise Http404("Not authorized")
    
    # Check if ticket can be edited (only Open or In Progress)
    if ticket.status not in ['Open', 'In Progress']:
        raise Http404("Ticket cannot be edited in current status")
    
    # Handle form submission
    if request.method == "POST":
        form = TicketForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            return redirect('dashboards:user_dashboard_page', page='tickets')
    else:
        form = TicketForm(instance=ticket)
    
    return render(
        request,
        'userdashboard/partials/ticket-edit.html',
        {"ticket": ticket, "form": form}
    )


@login_required
def agent_ticket_detail(request, identifier: str):

    """Ticket detail view for agents.



    Allows viewing a ticket if the logged-in user is staff/superuser OR

    is the assigned_to agent OR the ticket creator.

    Accepts the same identifier formats as admin_ticket_detail.

    """

    user = request.user

    ticket = None

    num = identifier.lstrip('#')

    if num.isdigit():

        ticket = Ticket.objects.filter(pk=int(num)).first()

    if ticket is None:

        candidates = []

        base = num

        if base:

            candidates.extend([base, f"TCK-{base}", f"#TCK-{base}"])

        raw = identifier

        if raw:

            candidates.extend([raw.lstrip('#'), raw, f"TCK-{raw.lstrip('#')}"])

        for cid in candidates:

            t = Ticket.objects.filter(ticket_id=cid).first()

            if t:

                ticket = t

                break

    if ticket is None:

        raise Http404("Ticket not found")



    # Permission: ticket must be assigned to this agent or created by them,
    # and user must have agent role - STRICT CHECK
    if not is_agent_user(request):
        # Log the unauthorized access attempt
        role_name = getattr(request.user.userprofile.role, 'name', 'No profile') if hasattr(request.user, 'userprofile') and getattr(request.user.userprofile, 'role', None) else 'No profile'
        logger.warning(f"Unauthorized access attempt by {request.user.username} (role: {role_name}) to agent ticket detail: {identifier}")
        
        # Return 404 for unauthorized access
        raise Http404("Not authorized")
    
    # Additional permission check: ticket must be assigned to this agent
    if ticket.assigned_to != user and ticket.created_by != user:
        raise Http404("Not authorized - Ticket not assigned to you")



    return render(

        request,

        'admindashboard/partials/ticket-detail.html',

        {"ticket": ticket}

    )





@login_required

def user_ticket_detail(request, identifier: str):

    """Ticket detail view for end-users on the user dashboard.



    Accepts the same identifier formats as admin_ticket_detail/agent_ticket_detail

    and only allows access if the logged-in user is the ticket creator.

    """

    user = request.user

    ticket = None



    # Try numeric PK first (strip leading '#')

    num = identifier.lstrip('#')

    if num.isdigit():

        ticket = Ticket.objects.filter(pk=int(num)).first()



    # Fallback to ticket_id variants

    if ticket is None:

        candidates = []

        base = num

        if base:

            candidates.extend([base, f"TCK-{base}", f"#TCK-{base}"])

        raw = identifier

        if raw:

            candidates.extend([raw.lstrip('#'), raw, f"TCK-{raw.lstrip('#')}"])

        for cid in candidates:

            t = Ticket.objects.filter(ticket_id=cid).first()

            if t:

                ticket = t

                break



    if ticket is None:

        raise Http404("Ticket not found")



    # Permission: only the creator can view this ticket from user dashboard

    if ticket.created_by != user and not (user.is_staff or user.is_superuser):

        raise Http404("Not authorized")



    return render(

        request,

        'admindashboard/partials/ticket-detail.html',

        {"ticket": ticket}

    )





@login_required

def admin_ticket_edit(request, identifier: str):

    is_role_admin = False

    if hasattr(request.user, "userprofile") and getattr(request.user.userprofile, "role", None):

        is_role_admin = (getattr(request.user.userprofile.role, "name", "").lower() == "admin")

    if not (request.user.is_superuser or request.user.is_staff or is_role_admin):

        raise Http404("Not authorized")



    # Resolve identifier to a Ticket instance (numeric pk or ticket_id variants)

    ticket = None

    num = identifier.lstrip('#')

    if num.isdigit():

        ticket = Ticket.objects.filter(pk=int(num)).first()

    if ticket is None:

        candidates = []

        base = num

        if base:

            candidates.extend([base, f"TCK-{base}", f"#TCK-{base}"])

        raw = identifier

        if raw:

            candidates.extend([raw.lstrip('#'), raw, f"TCK-{raw.lstrip('#')}"])

        for cid in candidates:

            t = Ticket.objects.filter(ticket_id=cid).first()

            if t:

                ticket = t

                break

    if ticket is None:
        raise Http404("Ticket not found")

    # Use AdminTicketForm for editing inside the modal
    if request.method == "POST":
        form = AdminTicketForm(request.POST, instance=ticket)
        
        if form.is_valid():
            ticket_obj = form.save(commit=False)
            
            # If ticket is assigned to an agent, change status to "In Progress"
            if ticket_obj.assigned_to and ticket_obj.status == 'Open':
                ticket_obj.status = 'In Progress'
            
            ticket_obj.save()
            
            messages.success(request, f"Ticket '{ticket.ticket_id}' has been updated and assigned to {ticket_obj.assigned_to.get_full_name() if ticket_obj.assigned_to else 'Unassigned'}.")
            
            return redirect('dashboards:admin_dashboard_page', page='tickets.html')
    else:
        form = AdminTicketForm(instance=ticket)



    return render(
        request,
        'admindashboard/partials/ticket-edit.html',
        {"ticket": ticket, "form": form}
    )





class SiteSettingsView(APIView):

    def _is_admin(self, user):

        if not user or not user.is_authenticated:

            return False

        if user.is_superuser or user.is_staff:

            return True

        try:

            role = getattr(getattr(user, 'userprofile', None), 'role', None)

            return (getattr(role, 'name', '').lower() == 'admin')

        except Exception:

            return False



    def get(self, request):

        if not self._is_admin(request.user):

            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)



        s = SiteSettings.get_solo()

        data = {

            'company_name': s.company_name,

            'website_url': s.website_url,

            'contact_email': s.contact_email,

            'contact_phone': s.contact_phone,

            'address': s.address,

            'default_language': s.default_language,

            'time_zone': s.time_zone,

            'date_format': s.date_format,

            'time_format': s.time_format,

            'first_day_of_week': s.first_day_of_week,

            'currency': s.currency,

            'maintenance_mode': s.maintenance_mode,

            'user_registration': s.user_registration,

            'email_verification': s.email_verification,

            'remember_me': s.remember_me,

            'show_tutorial': s.show_tutorial,

            'theme': s.theme,

            'primary_color': s.primary_color,

            'fixed_header': s.fixed_header,

            'fixed_sidebar': s.fixed_sidebar,

            'collapsed_sidebar': s.collapsed_sidebar,

            'company_logo': (s.company_logo.url if getattr(s, 'company_logo', None) else ''),

            'collapsed_logo': getattr(s, 'collapsed_logo', False),

            # ticket settings

            'default_ticket_status': s.default_ticket_status,

            'default_ticket_priority': s.default_ticket_priority,

            'auto_ticket_assignment': s.auto_ticket_assignment,

            'allow_ticket_reopen': s.allow_ticket_reopen,

            'first_response_hours': s.first_response_hours,

            'resolution_time_hours': s.resolution_time_hours,

            'sla_business_hours': s.sla_business_hours,

        }

        return Response(data, status=status.HTTP_200_OK)



    def patch(self, request):

        if not self._is_admin(request.user):

            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)



        try:

            s = SiteSettings.get_solo()

            data = request.data or {}



            # Text fields

            text_fields = [

                'company_name', 'website_url', 'contact_email', 'contact_phone',

                'address', 'default_language', 'time_zone', 'date_format',

                'time_format', 'currency', 'theme', 'primary_color',

                'default_ticket_status', 'default_ticket_priority', 'sla_business_hours',

            ]

            for field in text_fields:

                if field in data:

                    value = data.get(field)

                    setattr(s, field, '' if value is None else str(value))



            # Integer fields

            if 'first_day_of_week' in data:

                try:

                    s.first_day_of_week = int(data.get('first_day_of_week'))

                except (TypeError, ValueError):

                    pass

            if 'first_response_hours' in data:

                try:

                    s.first_response_hours = int(data.get('first_response_hours'))

                except (TypeError, ValueError):

                    pass

            if 'resolution_time_hours' in data:

                try:

                    s.resolution_time_hours = int(data.get('resolution_time_hours'))

                except (TypeError, ValueError):

                    pass



            # Helper to normalize booleans

            def to_bool(value):

                if isinstance(value, bool):

                    return value

                if value is None:

                    return False

                if isinstance(value, str):

                    return value.strip().lower() in ('1', 'true', 'yes', 'on')

                try:

                    return bool(int(value))

                except Exception:

                    return False



            bool_fields = [

                'maintenance_mode', 'user_registration', 'email_verification',

                'remember_me', 'show_tutorial', 'fixed_header',

                'fixed_sidebar', 'collapsed_sidebar',

                'auto_ticket_assignment', 'allow_ticket_reopen',

            ]

            for field in bool_fields:

                if field in data:

                    setattr(s, field, to_bool(data.get(field)))



            # Handle company_logo update (accept base64 data URL)

            if 'company_logo' in data:

                company_logo_data = data.get('company_logo') or ''

                if isinstance(company_logo_data, str) and company_logo_data.startswith('data:image'):

                    try:

                        header, encoded = company_logo_data.split(',', 1)

                        decoded = base64.b64decode(encoded)

                        ext = 'png'

                        if 'jpeg' in header or 'jpg' in header:

                            ext = 'jpg'

                        elif 'gif' in header:

                            ext = 'gif'

                        filename = f"site_logo_{uuid.uuid4().hex}.{ext}"

                        s.company_logo.save(filename, ContentFile(decoded), save=False)

                    except Exception:

                        pass

                elif company_logo_data is None or company_logo_data == '':

                    # clear logo

                    try:

                        if getattr(s, 'company_logo'):

                            s.company_logo.delete(save=False)

                    except Exception:

                        pass



            if 'collapsed_logo' in data:

                s.collapsed_logo = to_bool(data.get('collapsed_logo'))



            s.save()

            return Response({'detail': 'saved'}, status=status.HTTP_200_OK)



        except Exception as exc:

            return Response(

                {

                    'detail': 'Server error while saving settings',

                    'error': str(exc),

                },

                status=status.HTTP_500_INTERNAL_SERVER_ERROR,

            )











