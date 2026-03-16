from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login, logout

from django.contrib import messages

from .forms import LoginForm, SignupForm

from .models import UserProfile, Role

from django.core.mail import send_mail

from django.contrib.auth.models import User

from django.conf import settings

from django.utils.crypto import get_random_string

from rest_framework.views import APIView

from rest_framework.response import Response

from rest_framework import status

from rest_framework.permissions import IsAuthenticated

from django.contrib.auth.password_validation import validate_password

from rest_framework_simplejwt.tokens import RefreshToken

from django.db import models

from django.db.models import Count

from tickets.models import Ticket, ChatMessage, MutedChat

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from django.utils.encoding import force_bytes

from django.contrib.auth.tokens import default_token_generator

from django.contrib.auth import get_user_model

from django.utils.http import urlsafe_base64_decode

from django.contrib.auth import authenticate, login



User = get_user_model()

import re

import random

from django.utils import timezone



# temporary in-memory store for password reset tokens (development only)

reset_links = {}



# Create your views here.



def login_view(request):

    errors = {}

    request_post = request.POST if request.method == 'POST' else {}



    if request.method == 'POST':

        username_or_email = request.POST.get('username', '').strip()

        password = request.POST.get('password', '').strip()



        user = None

        if username_or_email:

            # First check if user exists and is inactive (before authentication)

            try:

                # Try username first

                potential_user = User.objects.filter(username=username_or_email).first()

                if not potential_user:

                    # Try email lookup

                    potential_user = User.objects.filter(email=username_or_email).first()

                

                if potential_user:

                    # Check if user is inactive (Django User field)

                    if not potential_user.is_active:

                        # Check user role for specific message

                        if hasattr(potential_user, 'userprofile') and potential_user.userprofile:

                            if getattr(potential_user.userprofile.role, 'name', '').lower() == 'agent':

                                errors['invalid'] = "Agent account is inactive"

                            elif getattr(potential_user.userprofile.role, 'name', '').lower() in ['admin', 'superadmin']:

                                errors['invalid'] = "Admin account is inactive"

                            else:

                                errors['invalid'] = "User account is inactive"

                        else:

                            errors['invalid'] = "User account is inactive"

                        return render(request, 'login.html', {'errors': errors, 'request_post': request_post})

                    

                    # Check if user profile is inactive (UserProfile field)

                    user_profile = getattr(potential_user, 'userprofile', None)

                    if user_profile and not user_profile.is_active:

                        # Check user role for specific message

                        if getattr(user_profile.role, 'name', '').lower() == 'agent':

                            errors['invalid'] = "Agent account is inactive"

                        elif getattr(user_profile.role, 'name', '').lower() in ['admin', 'superadmin']:

                            errors['invalid'] = "Admin account is inactive"

                        else:

                            errors['invalid'] = "User account is inactive"

                        return render(request, 'login.html', {'errors': errors, 'request_post': request_post})

            except:

                pass

            

            # Now authenticate (only for active users)

            user = authenticate(request, username=username_or_email, password=password)

            if not user:

                # Try email - use first() instead of get() to handle multiple users with same email

                try:

                    u = User.objects.filter(email=username_or_email).first()

                    if u:

                        user = authenticate(request, username=u.username, password=password)

                except:

                    user = None



        if user:

            if not user.is_active:

                # Check user role for specific message

                if _is_agent(user):

                    errors['invalid'] = "Agent account is inactive"

                elif _is_admin(user):

                    errors['invalid'] = "Admin account is inactive"

                else:

                    errors['invalid'] = "User account is inactive"

            else:

                # Check if user profile is active (UserProfile field)

                user_profile = getattr(user, 'userprofile', None)

                if user_profile and not user_profile.is_active:

                    # Check user role for specific message

                    if _is_agent(user):

                        errors['invalid'] = "Agent account is inactive"

                    elif _is_admin(user):

                        errors['invalid'] = "Admin account is inactive"

                    else:

                        errors['invalid'] = "User account is inactive"

                else:

                    login(request, user)

                    # Redirect based on role

                    if _is_admin(user):

                        return redirect('dashboards:admin_dashboard')

                    if _is_agent(user):

                        return redirect('dashboards:agent_dashboard_index')

                    return redirect('dashboards:user_dashboard')

        else:

            errors['invalid'] = "Invalid username/email or password"



    return render(request, 'login.html', {'errors': errors, 'request_post': request_post})



def logout_view(request):
    
    # Store user role before logout
    user_role = None
    if request.user.is_authenticated:
        if _is_admin(request.user):
            user_role = 'admin'
        elif _is_agent(request.user):
            user_role = 'agent'
        else:
            user_role = 'user'
    
    logout(request)
    
    messages.success(request, "Logged out successfully.")
    
    # Redirect based on user role
    if user_role == 'admin':
        return redirect('users:admin_login')
    elif user_role == 'agent':
        return redirect('users:agent_login')
    else:
        return redirect('users:user_login')





def forgot_password_view(request):

    if request.method == 'POST':

        email = (request.POST.get('email') or '').strip()



        user = User.objects.filter(email=email).first()

        if not user:

            return render(request, 'forgot_password.html', {'error': 'Email not registered'})



        code = f"{random.randint(0, 999999):06d}"

        request.session['fp_email'] = email

        request.session['fp_code'] = code

        request.session['fp_code_verified'] = False

        request.session['fp_code_ts'] = int(timezone.now().timestamp())



        send_mail(

            subject="Password Reset Code",

            message=f"Your password reset code is: {code}\n\nIf you did not request this, you can ignore this email.",

            from_email=settings.DEFAULT_FROM_EMAIL,

            recipient_list=[email],

            fail_silently=False,

        )



        return redirect('users:forgot_password_code')



    return render(request, 'forgot_password.html')





def forgot_password_code_view(request):

    email = request.session.get('fp_email')

    if not email:

        return redirect('users:forgot_password')



    if request.method == 'POST':

        code = (request.POST.get('code') or '').strip()

        expected = str(request.session.get('fp_code') or '')

        if not expected:

            return redirect('users:forgot_password')



        if code != expected:

            return render(request, 'verify_code.html', {'error': 'Invalid code. Please try again.'})



        request.session['fp_code_verified'] = True

        return redirect('users:forgot_password_new_password')



    return render(request, 'verify_code.html')





def forgot_password_new_password_view(request):

    email = request.session.get('fp_email')

    verified = bool(request.session.get('fp_code_verified'))

    if not email or not verified:

        return redirect('users:forgot_password')



    user = User.objects.filter(email=email).first()

    if not user:

        return redirect('users:forgot_password')



    if request.method == 'POST':

        password1 = (request.POST.get('password1') or '').strip()

        password2 = (request.POST.get('password2') or '').strip()



        if not password1 or not password2:

            return render(request, 'set_new_password.html', {'error': 'Please fill both password fields.'})



        if password1 != password2:

            return render(request, 'set_new_password.html', {'error': 'Passwords do not match.'})



        try:

            validate_password(password1, user=user)

        except Exception as e:

            return render(request, 'set_new_password.html', {'error': str(e)})



        user.set_password(password1)

        user.save()



        # Clear session data for reset flow

        for k in ['fp_email', 'fp_code', 'fp_code_verified', 'fp_code_ts']:

            request.session.pop(k, None)



        messages.success(request, 'Password updated successfully. Please log in.')

        return redirect('users:login')



    return render(request, 'set_new_password.html')



        





# SIGNUP

def signup_view(request):

    if request.method == 'POST':

        username = request.POST.get('username')

        email = request.POST.get('email')

        password = request.POST.get('password')

        confirm_password = request.POST.get('confirm_password')



        if password != confirm_password:

            messages.error(request, 'Passwords do not match')

            return redirect('users:signup')



        if User.objects.filter(username=username).exists():

            messages.error(request, 'Username already taken')

            return redirect('users:signup')



        user = User.objects.create_user(username=username, email=email, password=password)

        user.save()

        messages.success(request, 'Account created successfully. Please log in.')

        return redirect('users:login')



    return render(request, 'signup.html')





def forgot_password(request):

    if request.method == 'POST':

        email = request.POST.get('email')

        user = User.objects.filter(email=email).first()

        if user:

            token = get_random_string(32)

            reset_links[token] = user.username  # store temporarily



            reset_url = request.build_absolute_uri(f"/reset-password/{token}/")



            send_mail(

                'Password Reset Link',

                f'Click the following link to reset your password: {reset_url}',

                'yourgmail@gmail.com',

                [email],

                fail_silently=False,

            )



            messages.success(request, "Password reset link has been sent to your email.")

            return redirect('users:login')

        else:

            messages.error(request, "No account found with that email.")

    return render(request, 'forgot_password.html')









def reset_password(request, uidb64, token):

    try:

        uid = urlsafe_base64_decode(uidb64).decode()

        user = User.objects.get(pk=uid)

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):

        user = None



    if user is None or not default_token_generator.check_token(user, token):

        messages.error(request, "Invalid or expired reset link")

        return redirect('users:forgot_password')



    if request.method == "POST":

        password1 = request.POST.get('password1')

        password2 = request.POST.get('password2')



        if password1 != password2:

            messages.error(request, "Passwords do not match")

            return redirect(request.path)



        user.set_password(password1)

        user.save()

        messages.success(request, "Password reset successful! You can now login.")

        return redirect('users:login')



    return render(request, 'reset_password.html')











def _is_admin(user):

    if not user or not user.is_authenticated:

        return False

    if user.is_superuser:

        return True

    if hasattr(user, "userprofile") and getattr(user.userprofile, "role", None):

        return (getattr(user.userprofile.role, "name", "").lower() in ["admin", "superadmin"])

    return False





# def _is_agent(user):

#     if not user or not user.is_authenticated:

#         return False

#     if hasattr(user, "userprofile") and getattr(user.userprofile, "role", None):

#         return (getattr(user.userprofile.role, "name", "").lower() == "agent")

#     return False



def _is_agent(user):

    if not user or not user.is_authenticated:

        return False

    if hasattr(user, "userprofile") and getattr(user.userprofile, "role", None):

        return (getattr(user.userprofile.role, "name", "").lower() == "agent")

    return False





def admin_login_view(request):

    if request.method == 'POST':

        username = request.POST.get('username')

        password = request.POST.get('password')

        # Resolve username if an email was provided - improved logic

        lookup_username = username

        

        # If input contains '@', treat as email and lookup by email

        if '@' in username:

            try:

                email_user = User.objects.get(email=username)

                lookup_username = email_user.username

            except User.DoesNotExist:

                # Email not found, continue with original (might be username with @)

                pass

            except User.MultipleObjectsReturned:

                # Multiple users with same email - show generic error

                messages.error(request, 'Invalid username or password.')

                return render(request, 'login.html')

        else:

            # If input doesn't contain '@', try username first

            # If username doesn't exist, try treating it as email (in case email without @)

            if not User.objects.filter(username=username).exists():

                try:

                    email_user = User.objects.get(email=username)

                    lookup_username = email_user.username

                except User.DoesNotExist:

                    # Neither username nor email found

                    pass

                except User.MultipleObjectsReturned:

                    # Multiple users with same email - show generic error

                    messages.error(request, 'Invalid username or password.')

                    return render(request, 'login.html')

        user = authenticate(request, username=lookup_username, password=password)

        if user:

            # Check if user is active (Django User field)

            if not user.is_active:

                messages.error(request, 'Admin account is inactive')

                return render(request, 'login.html')

            

            # Check if user profile is active (UserProfile field)

            user_profile = getattr(user, 'userprofile', None)

            if user_profile and not user_profile.is_active:

                messages.error(request, 'Admin account is inactive')

                return render(request, 'login.html')

            

            # Check if user has Admin role

            if _is_admin(user):

                login(request, user)

                messages.success(request, "Admin login successful!")

                return redirect('dashboards:admin_dashboard')

            else:

                messages.error(request, 'Access denied. Admin role required.')

        else:

            # Authentication failed - check if user exists but is inactive

            try:

                potential_user = User.objects.get(username=lookup_username)

                if not potential_user.is_active:

                    messages.error(request, 'Admin account is inactive')

                    return render(request, 'login.html')

            except User.DoesNotExist:

                pass

            

            # Check if user exists by email and is inactive

            try:

                potential_user = User.objects.get(email=username)

                if not potential_user.is_active:

                    messages.error(request, 'Admin account is inactive')

                    return render(request, 'login.html')

            except User.DoesNotExist:

                pass

            

            messages.error(request, 'Invalid admin credentials')

    return render(request, 'login.html')





def agent_login_view(request):

    """Dedicated login view for Agents, similar to admin_login_view.



    Only users whose profile role is 'Agent' are allowed to log in here.

    Successful login redirects to the Agent dashboard.

    """

    if request.method == 'POST':

        username = request.POST.get('username')

        password = request.POST.get('password')



        # Allow email or username - improved logic

        lookup_username = username

        

        # If input contains '@', treat as email and lookup by email

        if '@' in username:

            try:

                email_user = User.objects.get(email=username)

                lookup_username = email_user.username

            except User.DoesNotExist:

                # Email not found, continue with original (might be username with @)

                pass

            except User.MultipleObjectsReturned:

                # Multiple users with same email - show generic error

                messages.error(request, 'Invalid username or password.')

                return render(request, 'login.html')

        else:

            # If input doesn't contain '@', try username first

            # If username doesn't exist, try treating it as email (in case email without @)

            if not User.objects.filter(username=username).exists():

                try:

                    email_user = User.objects.get(email=username)

                    lookup_username = email_user.username

                except User.DoesNotExist:

                    # Neither username nor email found

                    pass

                except User.MultipleObjectsReturned:

                    # Multiple users with same email - show generic error

                    messages.error(request, 'Invalid username or password.')

                    return render(request, 'login.html')



        user = authenticate(request, username=lookup_username, password=password)

        if user:

            # Check if user is active (Django User field)

            if not user.is_active:

                messages.error(request, 'Agent account is inactive')

                return render(request, 'login.html')

            

            # Check if user profile is active (UserProfile field)

            user_profile = getattr(user, 'userprofile', None)

            if user_profile and not user_profile.is_active:

                messages.error(request, 'Agent account is inactive')

                return render(request, 'login.html')

            

            # Check if user has Agent role

            if not _is_agent(user):

                messages.error(request, 'Access denied. Agent role required.')

                return render(request, 'login.html')

            

            login(request, user)

            messages.success(request, "Login successful!")

            # Reuse global role-based redirects

            if _is_admin(user):

                return redirect('dashboards:admin_dashboard')

            if _is_agent(user):

                return redirect('dashboards:agent_dashboard_index')

            return redirect('dashboards:user_dashboard')

        else:

            # Authentication failed - check if user exists but is inactive

            try:

                potential_user = User.objects.get(username=lookup_username)

                if not potential_user.is_active:

                    messages.error(request, 'Agent account is inactive')

                    return render(request, 'login.html')

            except User.DoesNotExist:

                pass

            

            # Check if user exists by email and is inactive

            try:

                potential_user = User.objects.get(email=username)

                if not potential_user.is_active:

                    messages.error(request, 'Agent account is inactive')

                    return render(request, 'login.html')

            except User.DoesNotExist:

                pass



        messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')





class AgentLoginAPIView(APIView):

    """API endpoint for agent login with proper HTTP status codes"""

    

    def post(self, request):

        # Get email and password from request data

        email = request.data.get('email')

        password = request.data.get('password')

        

        # Check for missing fields

        if not email or not password:

            return Response(

                {"error": "Email and password are required"},

                status=status.HTTP_400_BAD_REQUEST

            )

        

        # Allow email or username lookup

        lookup_username = email

        if '@' in email or not User.objects.filter(username=email).exists():

            try:

                email_user = User.objects.get(email=email)

                lookup_username = email_user.username

            except User.DoesNotExist:

                pass

            except User.MultipleObjectsReturned:

                # Multiple users with same email - return generic error

                return Response(

                    {"error": "Invalid email or password"},

                    status=status.HTTP_401_UNAUTHORIZED

                )

        

        # Authenticate user

        user = authenticate(request, username=lookup_username, password=password)

        

        if not user:

            # Authentication failed - return 401 with generic error

            return Response(

                {"error": "Invalid email or password"},

                status=status.HTTP_401_UNAUTHORIZED

            )

        

        # Check if user is active

        if not user.is_active:

            return Response(

                {"error": "Account is inactive"},

                status=status.HTTP_401_UNAUTHORIZED

            )

        

        # Check if user has Agent role

        if not _is_agent(user):

            return Response(

                {"error": "Access denied. Agent role required."},

                status=status.HTTP_403_FORBIDDEN

            )

        

        # Login the user

        login(request, user)

        

        # Generate JWT tokens if available

        try:

            refresh = RefreshToken.for_user(user)

            return Response({

                "message": "Login successful",

                "user": {

                    "id": user.id,

                    "username": user.username,

                    "email": user.email,

                    "first_name": user.first_name,

                    "last_name": user.last_name,

                    "role": "Agent"

                },

                "tokens": {

                    "refresh": str(refresh),

                    "access": str(refresh.access_token)

                }

            }, status=status.HTTP_200_OK)

        except Exception:

            # Fallback if JWT is not configured

            return Response({

                "message": "Login successful",

                "user": {

                    "id": user.id,

                    "username": user.username,

                    "email": user.email,

                    "first_name": user.first_name,

                    "last_name": user.last_name,

                    "role": "Agent"

                }

            }, status=status.HTTP_200_OK)











def user_login_view(request):

    errors = {}  # dictionary to send errors to template

    if request.method == 'POST':

        username = request.POST.get('username')

        password = request.POST.get('password')



        # Resolve username if email is provided

        lookup_username = username

        if '@' in username or not User.objects.filter(username=username).exists():

            email_user = User.objects.filter(email=username).first()

            if email_user:

                lookup_username = email_user.username



        user = authenticate(request, username=lookup_username, password=password)

        if user:

            # Check if user is active (Django User field)

            if not user.is_active:

                errors['invalid'] = "User account is inactive"

                return render(request, 'login.html', {'errors': errors, 'request_post': request.POST})

            

            # Check if user profile is active (UserProfile field)

            user_profile = getattr(user, 'userprofile', None)

            if user_profile and not user_profile.is_active:

                errors['invalid'] = "User account is inactive"

                return render(request, 'login.html', {'errors': errors, 'request_post': request.POST})

            

            login(request, user)

            # Use the same role-based redirect rules as the main login_view.

            # Avoid relying on Django Groups/staff flags, since they are easy to mis-assign.

            if _is_admin(user):

                return redirect('dashboards:admin_dashboard')

            if _is_agent(user):

                return redirect('dashboards:agent_dashboard_index')

            return redirect('dashboards:user_dashboard')

        else:

            # Authentication failed - check if user exists but is inactive

            try:

                potential_user = User.objects.get(username=lookup_username)

                if not potential_user.is_active:

                    errors['invalid'] = "User account is inactive"

                    return render(request, 'login.html', {'errors': errors, 'request_post': request.POST})

            except User.DoesNotExist:

                pass

            

            # Check if user exists by email and is inactive

            try:

                potential_user = User.objects.get(email=username)

                if not potential_user.is_active:

                    errors['invalid'] = "User account is inactive"

                    return render(request, 'login.html', {'errors': errors, 'request_post': request.POST})

            except User.DoesNotExist:

                pass

            

            errors['invalid'] = "Invalid username or password"



    return render(request, 'login.html', {'errors': errors, 'request_post': request.POST})







def admin_signup_view(request):

    errors = {}

    if request.method == 'POST':

        username = request.POST.get('username', '').strip()

        email = request.POST.get('email', '').strip()

        password = request.POST.get('password', '')

        confirm_password = request.POST.get('confirm_password', '')



        # --- Validations ---

        if not username:

            errors['username'] = "Username is required."

        elif User.objects.filter(username=username).exists():

            errors['username'] = "Username already taken."



        if not email:

            errors['email'] = "Email is required."

        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):

            errors['email'] = "Enter a valid email address."

        elif User.objects.filter(email=email).exists():

            errors['email'] = "Email already exists."



        if not password:

            errors['password'] = "Password is required."

        elif len(password) < 6:

            errors['password'] = "Password must be at least 6 characters."



        if password != confirm_password:

            errors['confirm_password'] = "Passwords do not match."



        # If any errors, render the form with errors

        if errors:

            return render(request, 'signup.html', {'errors': errors, 'request_post': request.POST})



        # --- Create Admin User ---

        user = User.objects.create_user(username=username, email=email, password=password)

        user.is_staff = True

        user.save()



        # Assign admin role to profile

        role, _ = Role.objects.get_or_create(name='Admin')

        profile = getattr(user, 'userprofile', None)

        if not profile:

            profile = UserProfile.objects.create(user=user, role=role)

        else:

            profile.role = role

            profile.save()



        messages.success(request, 'Admin account created. Please log in.')

        return redirect('users:admin_login')



    return render(request, 'signup.html')









def user_signup_view(request):

    errors = {}



    if request.method == "POST":

        first_name = request.POST.get('first_name', '').strip()

        last_name = request.POST.get('last_name', '').strip()

        username = request.POST.get('username', '').strip()

        email = request.POST.get('email', '').strip()

        password = request.POST.get('password', '')

        confirm_password = request.POST.get('password_confirm', '')



        # ---------- VALIDATIONS ----------



        if not first_name:

            errors['first_name'] = "First name is required"



        if not last_name:

            errors['last_name'] = "Last name is required"



        if not username:

            errors['username'] = "Username is required"

        elif User.objects.filter(username=username).exists():

            errors['username'] = "Username already exists"



        if not email:

            errors['email'] = "Email is required"

        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):

            errors['email'] = "Enter a valid email address"

        elif User.objects.filter(email=email).exists():

            errors['email'] = "Email already registered"



        if not password:

            errors['password'] = "Password is required"

        elif len(password) < 6:

            errors['password'] = "Password must be at least 6 characters"



        if password != confirm_password:

            errors['password_confirm'] = "Passwords do not match"



        # ---------- CREATE USER ----------

        if not errors:

            user = User.objects.create_user(

                username=username,

                email=email,

                password=password,

                first_name=first_name,

                last_name=last_name

            )



            # Assign USER role

            role, _ = Role.objects.get_or_create(name='User')

            UserProfile.objects.get_or_create(user=user, defaults={'role': role})



            return redirect('users:user_login')



    return render(request, 'signup.html', {'errors': errors})





def agent_signup_view(request):

    """Self-signup endpoint for Agents.



    Creates a normal Django user and assigns the Agent role via UserProfile,

    then redirects to the shared login where role-based redirect will send

    them to the Agent dashboard.

    """

    if request.method == 'POST':

        username = request.POST.get('username')

        email = request.POST.get('email')

        password = request.POST.get('password')

        confirm_password = request.POST.get('confirm_password')



        if password != confirm_password:

            messages.error(request, 'Passwords do not match')

            return redirect('users:agent_signup')



        if User.objects.filter(username=username).exists():

            messages.error(request, 'Username already taken')

            return redirect('users:agent_signup')



        if email and User.objects.filter(email=email).exists():

            messages.error(request, 'Email already in use')

            return redirect('users:agent_signup')



        user = User.objects.create_user(username=username, email=email, password=password)

        user.save()



        # Attach Agent role to profile

        role, _ = Role.objects.get_or_create(name='Agent')

        profile = getattr(user, 'userprofile', None)

        if not profile:

            UserProfile.objects.create(user=user, role=role)

        else:

            profile.role = role

            profile.save()



        messages.success(request, 'Agent account created successfully. Please log in.')

        # Use generic login; role-based redirects will handle destination

        return redirect('users:login')



    return render(request, 'signup.html')



class RegisterView(APIView):

    def post(self, request):

        username = request.data.get('username')

        email = request.data.get('email')

        password = request.data.get('password')

        confirm_password = request.data.get('confirm_password')



        if password != confirm_password:

            return Response({'error': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():

            return Response({'error': 'Username already taken.'}, status=status.HTTP_400_BAD_REQUEST)

        try:

            validate_password(password)

        except Exception as e:

            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, email=email, password=password)

        user.save()

        refresh = RefreshToken.for_user(user)

        return Response({

            'refresh': str(refresh),

            'access': str(refresh.access_token),

            'user': {

                'username': user.username,

                'email': user.email,

            }

        }, status=status.HTTP_201_CREATED)





class AgentsListView(APIView):

    def get(self, request):

        # Restrict to admins

        if not _is_admin(request.user):

            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

        # Consider agents as users whose role is specifically Agent (exclude Admin and other roles)

        qs = (

            User.objects

            .select_related('userprofile', 'userprofile__role')

            .annotate(tickets_count=Count('assigned_tickets'))

            .filter(

                userprofile__role__name='Agent'

            )

            .order_by('username')

        )

        data = []

        for u in qs:

            role_name = getattr(getattr(getattr(u, 'userprofile', None), 'role', None), 'name', '')

            department = getattr(getattr(u, 'userprofile', None), 'department', '') or ''

            is_active = getattr(getattr(u, 'userprofile', None), 'is_active', True)

            data.append({

                'id': u.id,

                'username': u.username,  # Add username for login reference

                'name': u.get_full_name() or u.username,

                'email': u.email,

                'role': role_name,

                'department': department,

                'tickets_count': u.tickets_count or 0,

                'is_active': bool(is_active),

                'initials': (u.get_full_name() or u.username)[:2].upper(),

            })

        return Response({'results': data, 'total': len(data), 'active': sum(1 for a in data if a['is_active'])})



    def post(self, request):

        """Create a new agent user from the Add Agent modal."""

        if not _is_admin(request.user):

            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)



        name = (request.data.get('name') or '').strip()

        email = (request.data.get('email') or '').strip()

        password = (request.data.get('password') or '').strip()

        role_name = (request.data.get('role') or 'Agent').strip()

        department = (request.data.get('department') or '').strip()

        is_active_raw = request.data.get('is_active', True)

        initials = (request.data.get('initials') or '').strip()



        if not name or not email:

            return Response({'detail': 'Name and email are required.'}, status=status.HTTP_400_BAD_REQUEST)



        if not password:

            return Response({'detail': 'Password is required.'}, status=status.HTTP_400_BAD_REQUEST)



        # Use email as username if unique, otherwise add a clear suffix
        username = email.split('@')[0] if '@' in email else name.replace(' ', '').lower()
        base_username = username or 'agent'

        # Ensure username is unique
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1



        # Use the provided password instead of generating a random one

        # Generate a simple random password; in real systems you'd email a reset link

        # random_password = get_random_string(10)



        is_active = True

        if isinstance(is_active_raw, str):

            is_active = is_active_raw.strip().lower() in ['1', 'true', 'yes', 'on']

        elif isinstance(is_active_raw, bool):

            is_active = is_active_raw



        try:

            user = User.objects.create_user(username=username, email=email, password=password)



            # Populate first_name and last_name from the provided full name for agents

            if name:

                parts = name.split()

                if len(parts) == 1:

                    user.first_name = parts[0]

                    user.last_name = ""

                else:

                    user.first_name = " ".join(parts[:-1])

                    user.last_name = parts[-1]



            # Agents are usually staff

            user.is_staff = True

            user.is_active = True

            user.save()



            # Normalize incoming role_name to valid Role.ROLE_CHOICES values

            normalized_role = role_name

            if normalized_role.lower() == 'administrator':

                normalized_role = 'Admin'

            elif normalized_role.lower() == 'manager':

                # We currently do not have a separate Manager role; treat as Agent

                normalized_role = 'Agent'

            if normalized_role not in dict(Role.ROLE_CHOICES):

                normalized_role = 'Agent'



            role_obj, _ = Role.objects.get_or_create(name=normalized_role or 'Agent')

            profile, created = UserProfile.objects.get_or_create(user=user, defaults={'role': role_obj})

            if not created:

                profile.role = role_obj

            if department:

                profile.department = department

            profile.is_active = bool(is_active)

            if initials:

                # Store initials in a simple way: overload department suffix if no dedicated field exists

                # If you later add a separate initials field, update this accordingly.

                profile_initials = initials[:2].upper()

                # Avoid touching comments or unrelated fields

                try:

                    setattr(profile, 'initials', profile_initials)

                except Exception:

                    pass

            profile.save()

            



            # Return the created agent in the same shape as GET list

            role_display = getattr(getattr(profile, 'role', None), 'name', '') or ('Admin' if user.is_staff else '')

            created_data = {

                'id': user.id,

                'name': user.get_full_name() or user.username,

                'username': user.username,  # Add username for login reference

                'email': user.email,

                'role': role_display,

                'department': getattr(profile, 'department', '') or '',

                'tickets_count': 0,

                'is_active': bool(profile.is_active),

                'initials': initials[:2].upper() if initials else (user.get_full_name() or user.username)[:2].upper(),

            }

            return Response(created_data, status=status.HTTP_201_CREATED)

        except Exception as exc:

            return Response({'detail': 'Failed to create agent', 'error': str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





class CustomersListView(APIView):

    def get(self, request):

        print(f"DEBUG: CustomersListView - User: {request.user}")
        print(f"DEBUG: CustomersListView - Is authenticated: {request.user.is_authenticated}")
        print(f"DEBUG: CustomersListView - Is admin: {_is_admin(request.user)}")

        # Restrict to admins only

        if not _is_admin(request.user):

            print("DEBUG: CustomersListView - User is not admin, returning 403")
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

        print("DEBUG: CustomersListView - User is admin, proceeding with query")



        # Get pagination parameters

        page = int(request.GET.get('page', 1))

        page_size = int(request.GET.get('page_size', 10))

        search = request.GET.get('search', '').strip()

        

        # Consider customers/end users as non-staff users whose role is 'User'

        qs = (

            User.objects

            .select_related('userprofile', 'userprofile__role')

            .annotate(

                # tickets created by this user (Ticket.created_by -> created_tickets)

                tickets_count=Count('created_tickets', distinct=True)

            )

            .filter(

                models.Q(is_staff=False),

                models.Q(userprofile__role__name='User')

            )

        )

        

        # Apply search filter

        if search:

            qs = qs.filter(

                models.Q(username__icontains=search) |

                models.Q(first_name__icontains=search) |

                models.Q(last_name__icontains=search) |

                models.Q(email__icontains=search) |

                models.Q(userprofile__phone__icontains=search)

            )



        # Get total count before pagination

        total_count = qs.count()
        
        print(f"DEBUG: CustomersListView - Total customers found: {total_count}")
        print(f"DEBUG: CustomersListView - Query SQL: {qs.query}")

        # Apply pagination

        offset = (page - 1) * page_size

        qs = qs[offset:offset + page_size]



        results = []

        for u in qs:

            profile = getattr(u, 'userprofile', None)

            phone = getattr(profile, 'phone', '') if profile else ''

            is_active = getattr(profile, 'is_active', True) if profile is not None else True

            initials = (u.get_full_name() or u.username or '?')[:2].upper()

            results.append({

                'id': u.id,

                'name': u.get_full_name() or u.username,

                'email': u.email,

                'phone': phone,

                'tickets_count': getattr(u, 'tickets_count', 0) or 0,

                'is_active': bool(is_active),

                'initials': initials,

            })

        print(f"DEBUG: CustomersListView - Results count: {len(results)}")
        if results:
            print(f"DEBUG: CustomersListView - First result: {results[0]}")



        # Calculate pagination info

        total_pages = (total_count + page_size - 1) // page_size

        has_next = page < total_pages

        has_prev = page > 1



        return Response({

            'results': results,

            'total': total_count,

            'page': page,

            'page_size': page_size,

            'total_pages': total_pages,

            'has_next': has_next,

            'has_prev': has_prev,

            'active': sum(1 for c in results if c['is_active']),

        })





class UsersListView(APIView):

    def get(self, request):

        # Restrict to admins only

        if not _is_admin(request.user):

            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)



        # Get pagination parameters

        page = int(request.GET.get('page', 1))

        page_size = int(request.GET.get('page_size', 10))

        search = request.GET.get('search', '').strip()

        role_filter = request.GET.get('role', '').strip()

        status_filter = request.GET.get('status', '').strip()

        

        # Get all users with their profiles and roles

        qs = User.objects.select_related('userprofile', 'userprofile__role').order_by('username')

        

        # Apply search filter

        if search:

            qs = qs.filter(

                models.Q(username__icontains=search) |

                models.Q(first_name__icontains=search) |

                models.Q(last_name__icontains=search) |

                models.Q(email__icontains=search) |

                models.Q(userprofile__department__icontains=search)

            )

        

        # Apply role filter

        if role_filter and role_filter != 'All Roles':

            if role_filter == 'Administrator':

                qs = qs.filter(is_staff=True)

            elif role_filter == 'Agent':

                qs = qs.filter(userprofile__role__name='Agent')

            elif role_filter == 'Customer':

                qs = qs.filter(userprofile__role__name='User', is_staff=False)



        # Get total count before pagination

        total_count = qs.count()

        

        # Apply pagination

        offset = (page - 1) * page_size

        qs = qs[offset:offset + page_size]



        results = []

        for u in qs:

            profile = getattr(u, 'userprofile', None)

            role_obj = getattr(profile, 'role', None) if profile else None

            role_name = getattr(role_obj, 'name', '') or ('Admin' if u.is_staff else 'User')



            # Map role to display label and badge class

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

            

            # Apply status filter

            if status_filter and status_filter != 'All Status':

                if status_filter == 'Active' and not is_active:

                    continue

                elif status_filter == 'Inactive' and is_active:

                    continue

                elif status_filter == 'Suspended' and is_active:

                    continue

            

            status_label = 'Active' if is_active else 'Inactive'

            status_badge_class = 'bg-success' if is_active else 'bg-secondary'



            full_name = (u.get_full_name() or '').strip() or u.username

            initials = (full_name or '?')[:2].upper()



            last_login = u.last_login

            if last_login:

                last_login_display = last_login.strftime('%d %b %Y, %I:%M %p')

            else:

                last_login_display = 'Never'



            results.append({

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

                'is_active': is_active,

            })



        # Calculate pagination info

        total_pages = (total_count + page_size - 1) // page_size

        has_next = page < total_pages

        has_prev = page > 1



        return Response({

            'results': results,

            'total': total_count,

            'page': page,

            'page_size': page_size,

            'total_pages': total_pages,

            'has_next': has_next,

            'has_prev': has_prev,

            'active': sum(1 for u in results if u.get('is_active', False)),

        })





class UserDetailView(APIView):

    """Retrieve, update, or delete a single user for the admin Users page."""



    def get_object(self, user_id):

        try:

            return User.objects.select_related('userprofile', 'userprofile__role').get(id=user_id)

        except User.DoesNotExist:

            return None



    def get(self, request, user_id):

        if not _is_admin(request.user):

            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)



        u = self.get_object(user_id)

        if not u:

            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)



        profile = getattr(u, 'userprofile', None)

        role_obj = getattr(profile, 'role', None) if profile else None

        role_name = getattr(role_obj, 'name', '') or ('Admin' if u.is_staff else 'User')

        department = getattr(profile, 'department', '') if profile else ''

        is_active = getattr(profile, 'is_active', True) if profile is not None else u.is_active



        data = {

            'id': u.id,

            'username': u.username,

            'first_name': u.first_name,

            'last_name': u.last_name,

            'email': u.email,

            'role': role_name,

            'department': department or '-',

            'is_active': bool(is_active),

        }

        return Response(data, status=status.HTTP_200_OK)



    def patch(self, request, user_id):

        if not _is_admin(request.user):

            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)



        u = self.get_object(user_id)

        if not u:

            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)



        data = request.data or {}



        first_name = data.get('first_name')

        last_name = data.get('last_name')

        email = data.get('email')

        role_name = data.get('role')

        department = data.get('department')

        phone = data.get('phone')

        is_active_raw = data.get('is_active')



        if first_name is not None:

            u.first_name = first_name

        if last_name is not None:

            u.last_name = last_name

        if email is not None:

            u.email = email



        profile, _ = UserProfile.objects.get_or_create(user=u)



        if role_name:

            normalized_role = role_name

            if normalized_role.lower() == 'administrator':

                normalized_role = 'Admin'

            elif normalized_role.lower() == 'customer':

                normalized_role = 'User'

            if normalized_role not in dict(Role.ROLE_CHOICES):

                normalized_role = 'User'

            role_obj, _ = Role.objects.get_or_create(name=normalized_role)

            profile.role = role_obj



        if department is not None:

            profile.department = department



        if phone is not None:

            # store phone number on the profile if that field exists

            try:

                profile.phone = phone

            except Exception:

                pass



        if is_active_raw is not None:

            # normalize boolean-ish values ("true", "false", 1, 0, etc.)

            is_active = False

            if isinstance(is_active_raw, bool):

                is_active = is_active_raw

            elif isinstance(is_active_raw, str):

                is_active = is_active_raw.strip().lower() in ['1', 'true', 'yes', 'on', 'active']

            else:

                try:

                    is_active = bool(int(is_active_raw))

                except Exception:

                    is_active = False



            # keep both the Django user and profile in sync

            u.is_active = is_active

            try:

                profile.is_active = is_active

            except Exception:

                pass



        profile.save()

        u.save()



        return self.get(request, user_id)



    def delete(self, request, user_id):

        if not _is_admin(request.user):

            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)



        u = self.get_object(user_id)

        if not u:

            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)



        # Do not allow deleting yourself

        if request.user.id == u.id:

            return Response({'detail': 'You cannot delete your own account.'}, status=status.HTTP_400_BAD_REQUEST)



        u.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)





class RolesListView(APIView):

    """List all roles with user counts and display metadata for roles.html."""



    def get(self, request):

        if not _is_admin(request.user):

            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)



        # Base role metadata used for display on the frontend

        role_display_meta = {

            'SuperAdmin': {

                'label': 'Super Admin',

                'badge': 'System',

                'badge_class': 'bg-danger',

                'description': 'Highest level access. Can manage admins, agents, users, and system settings.',

                'deletable': False,

            },

            'Admin': {

                'label': 'Administrator',

                'badge': 'System',

                'badge_class': 'bg-primary',

                'description': 'Full access to all features and settings in the system.',

                'deletable': False,

            },

            'Agent': {

                'label': 'Agent',

                'badge': 'Default',

                'badge_class': 'bg-secondary',

                'description': 'Can manage assigned tickets and view basic reports.',

                'deletable': False,

            },

            'User': {

                'label': 'Customer',

                'badge': 'Default',

                'badge_class': 'bg-secondary',

                'description': 'Can create and view their own tickets. Limited access.',

                'deletable': False,

            },

        }



        roles_qs = (

            Role.objects

            .annotate(user_count=Count('userprofile'))

            .order_by('name')

        )



        roles_data = []

        for r in roles_qs:

            meta = role_display_meta.get(r.name, {})

            label = meta.get('label') or r.name

            badge = meta.get('badge') or 'Custom'

            badge_class = meta.get('badge_class') or 'bg-info'

            description = meta.get('description') or 'Custom role defined in the system.'

            deletable = meta.get('deletable', True)



            roles_data.append({

                'id': r.id,

                'name': r.name,

                'label': label,

                'badge': badge,

                'badge_class': badge_class,

                'description': description,

                'user_count': r.user_count or 0,

                'deletable': bool(deletable),

            })



        return Response({'results': roles_data})





class RoleDetailView(APIView):

    """Detail operations for a single role (e.g., delete)."""



    def delete(self, request, role_id):

        if not _is_admin(request.user):

            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)



        try:

            role = Role.objects.get(id=role_id)

        except Role.DoesNotExist:

            return Response({'detail': 'Role not found'}, status=status.HTTP_404_NOT_FOUND)



        # Do not allow deleting core roles

        if role.name in ['SuperAdmin', 'Admin', 'Agent', 'User']:

            return Response({'detail': 'Cannot delete core system roles.'}, status=status.HTTP_400_BAD_REQUEST)



        # Prevent deletion if any profiles are still using this role

        if role.userprofile_set.exists():

            return Response({'detail': 'Cannot delete role that is assigned to users.'}, status=status.HTTP_400_BAD_REQUEST)



        role.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)





class ChatMessagesView(APIView):

    """List and create chat messages between the current user and a contact."""



    def get(self, request):

        if not request.user.is_authenticated:

            return Response({'detail': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)



        support_qs = User.objects.filter(

            models.Q(is_staff=True)

            | models.Q(is_superuser=True)

            | models.Q(userprofile__role__name__in=['SuperAdmin', 'Admin', 'Agent'])

        )

        is_support_user = request.user.is_staff or request.user.is_superuser or support_qs.filter(id=request.user.id).exists()



        contact_id = request.query_params.get('contact_id')

        ticket_id = (request.query_params.get('ticket_id') or '').strip()

        if not contact_id:

            return Response({'detail': 'contact_id is required'}, status=status.HTTP_400_BAD_REQUEST)



        try:

            other = User.objects.get(id=contact_id)

        except User.DoesNotExist:

            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)



        if not ticket_id:

            if is_support_user:

                ticket_id = (

                    ChatMessage.objects.filter(

                        (

                            models.Q(sender=other, recipient__in=support_qs)

                            | models.Q(recipient=other, sender__in=support_qs)

                        )

                    )

                    .exclude(ticket_id__isnull=True)

                    .exclude(ticket_id='')

                    .order_by('-created_at')

                    .values_list('ticket_id', flat=True)

                    .first()

                ) or (

                    Ticket.objects.filter(created_by=other)

                    .order_by('-created_at')

                    .values_list('ticket_id', flat=True)

                    .first()

                )

            else:

                ticket_id = (

                    Ticket.objects.filter(created_by=request.user)

                    .order_by('-created_at')

                    .values_list('ticket_id', flat=True)

                    .first()

                )

            ticket_id = (ticket_id or '').strip()



        # If the requester is a non-staff user, ensure the ticket belongs to them

        if not is_support_user:

            if not ticket_id:

                return Response({'results': []}, status=status.HTTP_200_OK)

            owns = Ticket.objects.filter(ticket_id=ticket_id, created_by=request.user).exists()

            if not owns:

                return Response({'detail': 'Ticket not found'}, status=status.HTTP_404_NOT_FOUND)



        # Treat support as a pool of staff users so any admin can see/respond.

        if is_support_user:

            # Staff fetching messages with a customer: include messages between the customer and ANY staff.

            qs = ChatMessage.objects.filter(

                (

                    models.Q(sender=other, recipient__in=support_qs)

                    | models.Q(recipient=other, sender__in=support_qs)

                )

            ).filter(ticket_id=ticket_id).order_by('created_at')

        else:

            # Customer fetching messages: include messages between them and ANY staff.

            qs = ChatMessage.objects.filter(

                (

                    models.Q(sender=request.user, recipient__in=support_qs)

                    | models.Q(recipient=request.user, sender__in=support_qs)

                )

            ).filter(ticket_id=ticket_id).order_by('created_at')



        results = []

        for msg in qs:

            direction = 'sent' if msg.sender_id == request.user.id else 'received'

            message_data = {

                'id': msg.id,

                'text': msg.text,  # Keep raw Unicode text, no HTML escaping

                'direction': direction,

                'sender_id': msg.sender_id,  # Add sender_id for proper direction detection

                'is_read': msg.is_read,      # Add read status for WhatsApp-style indicators

                'time': msg.created_at.astimezone().strftime('%I:%M %p'),  # Formatted time for display

                'created_at': msg.created_at.isoformat(),  # ISO format for consistent parsing

                'ticket_id': msg.ticket_id,

            }

            # Add attachments if any
            attachments = []
            for attachment in msg.attachments.all():
                attachments.append({
                    'id': attachment.id,
                    'filename': attachment.filename,
                    'filesize': attachment.filesize,
                    'url': attachment.file.url,
                })
            
            if attachments:
                message_data['attachments'] = attachments

            results.append(message_data)



        return Response({'ticket_id': ticket_id, 'results': results}, status=status.HTTP_200_OK)



    def post(self, request):

        if not request.user.is_authenticated:

            return Response({'detail': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)



        support_qs = User.objects.filter(

            models.Q(is_staff=True)

            | models.Q(is_superuser=True)

            | models.Q(userprofile__role__name__in=['SuperAdmin', 'Admin', 'Agent'])

        )

        is_support_user = request.user.is_staff or request.user.is_superuser or support_qs.filter(id=request.user.id).exists()



        contact_id = request.data.get('contact_id')

        ticket_id = (request.data.get('ticket_id') or '').strip()

        text = (request.data.get('text') or '').strip()

        # Check if either text or files are provided
        files = request.FILES.getlist('files')
        if not contact_id or (not text and not files):

            return Response({'detail': 'contact_id and either text or files are required.'}, status=status.HTTP_400_BAD_REQUEST)



        try:

            other = User.objects.get(id=contact_id)

        except User.DoesNotExist:

            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)



        if not ticket_id:

            if is_support_user:

                ticket_id = (

                    ChatMessage.objects.filter(

                        (

                            models.Q(sender=other, recipient__in=support_qs)

                            | models.Q(recipient=other, sender__in=support_qs)

                        )

                    )

                    .exclude(ticket_id__isnull=True)

                    .exclude(ticket_id='')

                    .order_by('-created_at')

                    .values_list('ticket_id', flat=True)

                    .first()

                ) or (

                    Ticket.objects.filter(created_by=other)

                    .order_by('-created_at')

                    .values_list('ticket_id', flat=True)

                    .first()

                )

            else:

                ticket_id = (

                    Ticket.objects.filter(created_by=request.user)

                    .order_by('-created_at')

                    .values_list('ticket_id', flat=True)

                    .first()

                )

            ticket_id = (ticket_id or '').strip()

            if not ticket_id:

                return Response({'detail': 'ticket_id is required.'}, status=status.HTTP_400_BAD_REQUEST)



        if not is_support_user:

            owns = Ticket.objects.filter(ticket_id=ticket_id, created_by=request.user).exists()

            if not owns:

                return Response({'detail': 'Ticket not found'}, status=status.HTTP_404_NOT_FOUND)



        # When a customer sends, pick a default staff recipient so the message is addressable.

        # Staff-to-customer messages keep the explicit recipient.

        if not is_support_user:

            staff_recipient = (

                support_qs.filter(is_active=True)

                .order_by('id')

                .first()

            )

            if not staff_recipient:

                return Response({'detail': 'No support staff available'}, status=status.HTTP_400_BAD_REQUEST)

            other = staff_recipient



        # If staff is sending, contact_id is the customer (keep as-is).



        msg = ChatMessage.objects.create(

            sender=request.user,

            recipient=other,

            ticket_id=ticket_id,

            text=text or '',  # Allow empty text if files are provided

            is_read=False,

        )



        # Handle file attachments
        attachments = []
        if files:
            from tickets.models import ChatMessageAttachment
            for file in files:
                # Validate file size (10MB limit)
                if file.size > 10 * 1024 * 1024:
                    continue  # Skip files that are too large
                
                attachment = ChatMessageAttachment.objects.create(
                    message=msg,
                    file=file
                )
                attachments.append({
                    'id': attachment.id,
                    'filename': attachment.filename,
                    'filesize': attachment.filesize,
                    'url': attachment.file.url,
                })



        response_data = {

            'id': msg.id,

            'text': msg.text,

            'direction': 'sent',

            'time': msg.created_at.astimezone().strftime('%I:%M %p'),

            'created_at': msg.created_at.isoformat(),  # ISO format for consistent parsing

            'ticket_id': msg.ticket_id,

        }

        # Add attachments if any
        if attachments:
            response_data['attachments'] = attachments



        return Response(response_data, status=status.HTTP_201_CREATED)





class ChatThreadDetailView(APIView):

    """Detail operations for a single chat thread (e.g., archive, delete)."""



    def post(self, request, contact_id):

        if not request.user.is_authenticated:

            return Response({'detail': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)



        try:

            other = User.objects.get(id=contact_id)

        except User.DoesNotExist:

            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)



        action = request.data.get('action')

        if action == 'archive':

            MutedChat.objects.get_or_create(user=request.user, contact=other)

            return Response(status=status.HTTP_200_OK)

        if action == 'unarchive':

            MutedChat.objects.filter(user=request.user, contact=other).delete()

            return Response(status=status.HTTP_200_OK)



        return Response({'detail': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)



    def delete(self, request, contact_id):

        if not request.user.is_authenticated:

            return Response({'detail': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)



        try:

            other = User.objects.get(id=contact_id)

        except User.DoesNotExist:

            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)



        MutedChat.objects.filter(user=request.user, contact=other).delete()



        return Response(status=status.HTTP_204_NO_CONTENT)





@method_decorator(csrf_exempt, name='dispatch')
class SetUserPasswordView(APIView):

    """Set or reset password for a user (agent/customer) by admin."""

    permission_classes = [IsAuthenticated]

    def dispatch(self, request, *args, **kwargs):
        print(f"DEBUG: SetUserPasswordView.dispatch called")
        print(f"DEBUG: User: {request.user}, Authenticated: {request.user.is_authenticated}")
        print(f"DEBUG: Method: {request.method}")
        return super().dispatch(request, *args, **kwargs)

    

    def get_object(self, user_id):

        try:

            return User.objects.select_related('userprofile', 'userprofile__role').get(id=user_id)

        except User.DoesNotExist:

            return None



    def post(self, request, user_id):

        """Set new password for a user."""

        print(f"DEBUG: SetUserPasswordView.post called for user_id={user_id}")
        print(f"DEBUG: Request user: {request.user}, authenticated: {request.user.is_authenticated}")
        print(f"DEBUG: Request data: {request.data}")
        
        if not _is_admin(request.user):

            print(f"DEBUG: Admin check failed for user {request.user}")
            return Response({'detail': 'Forbidden - Admin access required'}, status=status.HTTP_403_FORBIDDEN)

        print(f"DEBUG: Admin check passed for user {request.user}")

        user = self.get_object(user_id)

        if not user:

            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        print(f"DEBUG: Target user found: {user.username}")

        password = request.data.get('password', '').strip()

        confirm_password = request.data.get('confirm_password', '').strip()

        print(f"DEBUG: Password length: {len(password)}, confirm length: {len(confirm_password)}")

        # Validation

        if not password:

            print("DEBUG: Password validation failed - empty password")
            return Response({'detail': 'Password is required'}, status=status.HTTP_400_BAD_REQUEST)

        

        if len(password) < 8:

            print("DEBUG: Password validation failed - too short")
            return Response({'detail': 'Password must be at least 8 characters long'}, status=status.HTTP_400_BAD_REQUEST)



        if password != confirm_password:

            print("DEBUG: Password validation failed - passwords don't match")
            return Response({'detail': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)



        try:

            # Validate password using Django's built-in validation

            from django.contrib.auth.password_validation import validate_password

            validate_password(password, user=user)
            print("DEBUG: Django password validation passed")

        except Exception as e:

            print(f"DEBUG: Django password validation failed: {str(e)}")
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)



        try:

            # Set password

            print("DEBUG: Attempting to set password")
            user.set_password(password)
            user.save()
            print("DEBUG: Password set successfully")

            

            # Log action for security auditing

            try:

                from django.contrib.admin.models import LogEntry, CHANGE

                LogEntry.objects.log_action(

                    user_id=request.user.id,

                    content_type_id=None,

                    object_id=user.id,

                    object_repr=f"{user.username} ({user.get_full_name() or user.email})",

                    action_flag=CHANGE,

                    change_message=f"Password set by admin: {request.user.username}"

                )

            except Exception:

                # Log entry is optional, continue if it fails

                pass



            return Response({

                'detail': 'Password set successfully',

                'user_id': user.id,

                'username': user.username,

                'email': user.email

            }, status=status.HTTP_200_OK)



        except Exception as e:

            print(f"DEBUG: Failed to set password: {str(e)}")
            return Response({'detail': f'Failed to set password: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



