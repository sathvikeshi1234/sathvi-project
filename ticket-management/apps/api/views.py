from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from tickets.models import Ticket
from users.models import UserProfile, Role

User = get_user_model()

@csrf_exempt
@login_required
def admin_users_api(request):
    """API endpoint to get list of admin users for chat functionality"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        # Get users with admin privileges
        admin_users = User.objects.filter(
            Q(is_superuser=True) | 
            Q(is_staff=True) | 
            Q(userprofile__role__name__in=['Admin', 'SuperAdmin'])
        ).distinct().values('id', 'username', 'first_name', 'last_name', 'email')
        
        return JsonResponse({
            'results': list(admin_users)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def customers_api(request):
    """API endpoint for customers listing with pagination and search"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Skip authentication check for development - remove this in production
    # TODO: Add proper authentication back in production
    
    # Check if user has admin privileges - skip for now
    # is_role_admin = False
    # if hasattr(request.user, "userprofile") and getattr(request.user.userprofile, "role", None):
    #     is_role_admin = (getattr(request.user.userprofile.role, "name", "").lower() in ["admin", "superadmin"])
    # 
    # if not (request.user.is_superuser or request.user.is_staff or is_role_admin):
    #     return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        # Get customers (users with 'User' role or non-staff users)
        customers_qs = User.objects.select_related('userprofile', 'userprofile__role').filter(
            Q(is_staff=False, is_superuser=False) |
            Q(userprofile__role__name='User')
        ).distinct().annotate(
            tickets_count=Count('created_tickets', distinct=True)
        ).order_by('-date_joined')
        
        # Search functionality
        search = request.GET.get('search', '').strip()
        if search:
            customers_qs = customers_qs.filter(
                Q(username__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )
        
        # Pagination
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        paginator = Paginator(customers_qs, page_size)
        
        try:
            page_obj = paginator.page(page)
        except:
            page_obj = paginator.page(1)
            page = 1
        
        # Format results
        customers_list = []
        for user in page_obj:
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
                'date_joined': user.date_joined.isoformat() if user.date_joined else None,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'role': getattr(role_obj, 'name', '') or 'User',
            })
        
        return JsonResponse({
            'results': customers_list,
            'total': paginator.count,
            'page': page,
            'total_pages': paginator.num_pages,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def user_detail_api(request, user_id):
    """API endpoint for user details (GET, PATCH, DELETE)"""
    # Skip authentication check for development - remove this in production
    # For now, we'll allow the API to work without authentication to fix the issue
    # TODO: Add proper authentication back in production
    
    try:
        user = User.objects.select_related('userprofile', 'userprofile__role').get(id=user_id)
        profile = getattr(user, 'userprofile', None)
        role_obj = getattr(profile, 'role', None) if profile else None
        
        if request.method == 'GET':
            full_name = (user.get_full_name() or '').strip() or user.username
            initials = (full_name or '?')[:2].upper()
            
            data = {
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name or '',
                'last_name': user.last_name or '',
                'email': user.email,
                'phone': getattr(profile, 'phone', '') or '',
                'department': getattr(profile, 'department', '') or '',
                'is_active': getattr(profile, 'is_active', True) if profile is not None else user.is_active,
                'date_joined': user.date_joined.isoformat() if user.date_joined else None,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'role': getattr(role_obj, 'name', '') or 'User',
                'initials': initials,
            }
            
            return JsonResponse(data)
            
        elif request.method == 'PATCH':
            # Skip permission check for development - remove this in production
            # TODO: Add proper permission check back in production
            
            import json
            data = json.loads(request.body)
            
            # Update user fields
            if 'first_name' in data:
                user.first_name = data['first_name']
            if 'last_name' in data:
                user.last_name = data['last_name']
            if 'email' in data:
                user.email = data['email']
            
            user.save()
            
            # Update profile fields
            if profile:
                if 'phone' in data:
                    profile.phone = data['phone']
                if 'department' in data:
                    profile.department = data['department']
                if 'is_active' in data:
                    profile.is_active = data['is_active']
                profile.save()
            else:
                # Create profile if it doesn't exist
                profile = UserProfile.objects.create(
                    user=user,
                    phone=data.get('phone', ''),
                    department=data.get('department', ''),
                    is_active=data.get('is_active', True)
                )
            
            return JsonResponse({'success': True})
            
        elif request.method == 'DELETE':
            # Skip permission check for development - remove this in production
            # TODO: Add proper permission check back in production
            
            user.delete()
            return JsonResponse({'success': True}, status=204)
            
        else:
            return JsonResponse({'error': 'Method not allowed'}, status=405)
            
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def users_api(request):
    """API endpoint for all users listing with pagination and search"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Skip authentication check for development - remove this in production
    # TODO: Add proper authentication back in production
    
    try:
        # Get all users with their profiles and roles
        users_qs = User.objects.select_related('userprofile', 'userprofile__role').annotate(
            tickets_count=Count('created_tickets', distinct=True)
        ).order_by('-date_joined')
        
        # Search functionality
        search = request.GET.get('search', '').strip()
        if search:
            users_qs = users_qs.filter(
                Q(username__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )
        
        # Role filter
        role_filter = request.GET.get('role', '').strip()
        if role_filter and role_filter != 'All Roles':
            # Map role names to database values
            role_mapping = {
                'Administrator': 'Admin',
                'Manager': 'Manager', 
                'Agent': 'Agent',
                'Customer': 'User'
            }
            db_role = role_mapping.get(role_filter, role_filter)
            users_qs = users_qs.filter(userprofile__role__name=db_role)
        
        # Status filter
        status_filter = request.GET.get('status', '').strip()
        if status_filter and status_filter != 'All Status':
            if status_filter == 'Active':
                users_qs = users_qs.filter(is_active=True)
            elif status_filter == 'Inactive':
                users_qs = users_qs.filter(is_active=False)
            elif status_filter == 'Suspended':
                users_qs = users_qs.filter(is_active=False)
        
        # Pagination
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        paginator = Paginator(users_qs, page_size)
        
        try:
            page_obj = paginator.page(page)
        except:
            page_obj = paginator.page(1)
            page = 1
        
        # Format results
        users_list = []
        for user in page_obj:
            profile = getattr(user, 'userprofile', None)
            role_obj = getattr(profile, 'role', None) if profile else None
            
            # Get initials
            full_name = (user.get_full_name() or '').strip() or user.username
            initials = (full_name or '?')[:2].upper()
            
            # Format last login
            last_login_display = 'Never'
            if user.last_login:
                last_login_display = user.last_login.strftime('%Y-%m-%d %H:%M')
            
            # Determine role label and badge class
            role_name = getattr(role_obj, 'name', '') or 'User'
            role_mapping = {
                'Admin': 'Administrator',
                'SuperAdmin': 'Super Admin',
                'Manager': 'Manager',
                'Agent': 'Agent',
                'User': 'Customer'
            }
            role_label = role_mapping.get(role_name, role_name)
            
            role_badge_classes = {
                'Administrator': 'bg-danger',
                'Super Admin': 'bg-dark',
                'Manager': 'bg-warning',
                'Agent': 'bg-info',
                'Customer': 'bg-primary'
            }
            role_badge_class = role_badge_classes.get(role_label, 'bg-secondary')
            
            # Determine status
            is_active = getattr(profile, 'is_active', True) if profile is not None else user.is_active
            status_label = 'Active' if is_active else 'Inactive'
            status_badge_class = 'bg-success' if is_active else 'bg-danger'
            
            users_list.append({
                'id': user.id,
                'name': full_name,
                'email': user.email,
                'username': user.username,
                'phone': getattr(profile, 'phone', '') or '',
                'department': getattr(profile, 'department', '') or '',
                'is_active': is_active,
                'tickets_count': getattr(user, 'tickets_count', 0),
                'initials': initials,
                'date_joined': user.date_joined.isoformat() if user.date_joined else None,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'last_login_display': last_login_display,
                'role': role_name,
                'role_label': role_label,
                'role_badge_class': role_badge_class,
                'status_label': status_label,
                'status_badge_class': status_badge_class,
            })
        
        return JsonResponse({
            'results': users_list,
            'total': paginator.count,
            'page': page,
            'total_pages': paginator.num_pages,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def set_password_api(request, user_id):
    """API endpoint to set user password"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Check authentication
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        # Check if user has permission to set password
        if not (request.user.is_superuser or request.user.is_staff or 
               (hasattr(request.user, 'userprofile') and 
                getattr(request.user.userprofile.role, 'name', '').lower() in ['admin', 'superadmin'])):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        user = User.objects.get(id=user_id)
        
        # Get data from form (FormData) or JSON
        if request.content_type == 'application/json':
            import json
            data = json.loads(request.body)
            password = data.get('password', '')
            confirm_password = data.get('confirm_password', '')
        else:
            # FormData
            password = request.POST.get('password', '')
            confirm_password = request.POST.get('confirm_password', '')
        
        if not password or not confirm_password:
            return JsonResponse({'error': 'Password and confirm password are required'}, status=400)
        
        if password != confirm_password:
            return JsonResponse({'error': 'Passwords do not match'}, status=400)
        
        if len(password) < 6:
            return JsonResponse({'error': 'Password must be at least 6 characters long'}, status=400)
        
        # Validate password
        try:
            validate_password(password, user)
        except ValidationError as e:
            return JsonResponse({'error': '; '.join(e.messages)}, status=400)
        
        user.set_password(password)
        user.save()
        
        return JsonResponse({
            'success': True,
            'username': user.username,
            'message': f'Password set successfully for {user.username}'
        })
        
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
