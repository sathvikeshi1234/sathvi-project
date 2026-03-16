from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from .models import Ticket, MutedChat, TicketAttachment, TicketStatusHistory, TicketComment
from .forms import TicketForm
from .serializers import DashboardStatsSerializer, RecentTicketSerializer, TicketSerializer, TicketCommentSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Avg
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

def record_status_change(ticket, old_status, new_status, changed_by_user):
    """
    Record a ticket status change in the audit trail.
    """
    if old_status != new_status:
        TicketStatusHistory.objects.create(
            ticket=ticket,
            old_status=old_status,
            new_status=new_status,
            changed_by=changed_by_user
        )

# Create your views here.
def ticket_list(request):
    if request.user.is_authenticated:
        if hasattr(request.user, "userprofile") and request.user.userprofile.role.name.lower() == "admin":
            tickets = Ticket.objects.all()
        else:
            tickets = Ticket.objects.filter(created_by=request.user)
    else:
        tickets = Ticket.objects.none()
    return render(request, "ticket_list.html", {"tickets": tickets})


@login_required
def ticket_create(request):
    if request.method == "POST":
        form = TicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            if ticket.category == "Others":
                other_value = request.POST.get("category_other", "").strip()
                if other_value:
                    ticket.category = other_value
            ticket.created_by = request.user
            ticket.save()

            # Record initial status in audit trail
            record_status_change(ticket, "Created", ticket.status, request.user)

            files = request.FILES.getlist('attachments')
            for f in files:
                TicketAttachment.objects.create(ticket=ticket, file=f)

            messages.success(request, "Ticket created successfully!")
            return redirect("dashboards:user_dashboard_page", page="tickets")
    else:
        form = TicketForm()
    # Template lives at tickets/templates/ticket_form.html
    return render(request, "ticket_form.html", {"form": form})


@login_required
def ticket_edit(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.user != ticket.created_by and request.user.userprofile.role.name.lower() != "admin":
        messages.error(request, "You don't have permission to edit this ticket.")
        return redirect("ticket_list")

    if request.method == "POST":
        old_status = ticket.status
        form = TicketForm(request.POST, instance=ticket)
        if form.is_valid():
            updated_ticket = form.save()
            
            # Record status change if it changed
            record_status_change(updated_ticket, old_status, updated_ticket.status, request.user)
            
            messages.success(request, "Ticket updated successfully!")
            return redirect("dashboards:admin_dashboard_page", page="tickets.html")
    else:
        form = TicketForm(instance=ticket)
    # Template lives at tickets/templates/ticket_form.html
    return render(request, "ticket_form.html", {"form": form, "ticket": ticket})


@login_required
def ticket_delete(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.user != ticket.created_by and request.user.userprofile.role.name.lower() != "admin":
        messages.error(request, "You don't have permission to delete this ticket.")
        return redirect("ticket_list")

    ticket.delete()
    messages.success(request, "Ticket deleted successfully!")
    # After delete, return to the admin dashboard tickets view
    return redirect("dashboards:admin_dashboard_page", page="tickets.html")



class DashboardStatsView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):

        today = timezone.now().date()

        total_tickets = Ticket.objects.count()
        open_tickets = Ticket.objects.filter(status="Open").count()
        resolved_today = Ticket.objects.filter(status="Resolved", updated_at__date=today).count()
        
        # No rating field on Ticket model; default to 0 for now
        avg_rating = 0

        distribution = {
            "open": Ticket.objects.filter(status="Open").count(),
            "in_progress": Ticket.objects.filter(status="In Progress").count(),
            "resolved": Ticket.objects.filter(status="Resolved").count(),
        }

        data = {
            "total_tickets": total_tickets,
            "open_tickets": open_tickets,
            "resolved_today": resolved_today,
            "avg_rating": round(avg_rating, 1),
            "distribution": distribution,
        }

        serializer = DashboardStatsSerializer(data)
        return Response(serializer.data)
    

class RecentTicketsView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        recent = Ticket.objects.order_by("-created_at")[:10]
        serializer = RecentTicketSerializer(recent, many=True)
        return Response(serializer.data)


@method_decorator(csrf_exempt, name='dispatch')
class TicketListCreateView(APIView):
    # Disable SessionAuthentication to avoid CSRF enforcement by DRF
    authentication_classes = []
    # GET requires auth; POST is allowed for anonymous (assigned to guest user)
    def get_permissions(self):
        # Allow unauthenticated access for GET and POST from the dashboard
        # (POST assigns to a 'guest' user; GET lists tickets for everyone)
        return [AllowAny()]
    def get(self, request):
        # Unauthenticated users see all tickets (demo/frontend dashboard)
        # Authenticated non-admin users see only their tickets; admins see all
        if not request.user.is_authenticated:
            qs = Ticket.objects.all().order_by("-created_at")
        elif (
            request.user.is_superuser
            or request.user.is_staff
            or (
                hasattr(request.user, "userprofile")
                and getattr(request.user.userprofile.role, "name", "").lower() == "admin"
            )
        ):
            qs = Ticket.objects.all().order_by("-created_at")
        else:
            qs = Ticket.objects.filter(created_by=request.user).order_by("-created_at")
        serializer = TicketSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TicketSerializer(data=request.data)
        if serializer.is_valid():
            # DRF authentication is disabled, so request.user will often be AnonymousUser.
            # Use the underlying Django request object to get the real logged-in user (if any).
            django_user = getattr(getattr(request, "_request", None), "user", None)

            creator = None
            # If a specific customer is provided (from dashboard modal), use or create that user
            customer_name = (request.data.get('customer') or request.data.get('customer_username') or '').strip()
            if customer_name:
                creator, _ = User.objects.get_or_create(username=customer_name, defaults={'email': ''})
                if not creator.has_usable_password():
                    # ensure no login via this demo account
                    creator.set_unusable_password()
                    creator.save()
            elif django_user and django_user.is_authenticated:
                # No separate customer: use the logged-in user as creator
                creator = django_user
            else:
                # Fallback to a guest user for anonymous submissions
                guest, created = User.objects.get_or_create(username='guest', defaults={'email': ''})
                if created:
                    guest.set_unusable_password()
                    guest.save()
                creator = guest

            # Create the ticket with the chosen creator
            ticket = serializer.save(created_by=creator)

            # Record initial status in audit trail
            record_status_change(ticket, None, ticket.status, django_user if django_user and django_user.is_authenticated else creator)

            # If there is a logged-in Django user and they are an Agent, assign the ticket to them
            # so it appears under their agentdashboard tickets and agenttickets pages.
            try:
                if django_user and getattr(django_user, 'is_authenticated', False):
                    profile = getattr(django_user, 'userprofile', None)
                    role_name = getattr(getattr(profile, 'role', None), 'name', '') if profile else ''
                    if role_name and role_name.lower() == 'agent':
                        ticket.assigned_to = django_user
                        ticket.save(update_fields=['assigned_to'])
            except Exception:
                # If anything goes wrong determining role/assignment, fail silently and keep ticket created_by only
                pass

            out = TicketSerializer(ticket)
            return Response(out.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TicketStatusUpdateView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    def patch(self, request, pk):
        ticket = get_object_or_404(Ticket, pk=pk)
        new_status = request.data.get("status")
        valid_status = [c[0] for c in Ticket.STATUS_CHOICES]
        if new_status not in valid_status:
            return Response({"detail": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)
        
        old_status = ticket.status
        ticket.status = new_status
        ticket.save()
        
        # Record the status change in audit trail
        django_user = getattr(getattr(request, "_request", None), "user", None)
        changed_by_user = django_user if django_user and django_user.is_authenticated else None
        record_status_change(ticket, old_status, new_status, changed_by_user)
        
        return Response({"status": ticket.status})


class MutedChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        contact_id = request.data.get('contact_id')
        if not contact_id:
            return Response({'detail': 'contact_id is required'}, status=400)
        try:
            contact = User.objects.get(id=contact_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=404)
        if MutedChat.objects.filter(user=request.user, contact=contact).exists():
            return Response({'detail': 'Already muted'}, status=400)
        MutedChat.objects.create(user=request.user, contact=contact)
        return Response({'detail': 'Muted'}, status=201)

    def delete(self, request):
        contact_id = request.data.get('contact_id') or request.query_params.get('contact_id')
        if not contact_id:
            return Response({'detail': 'contact_id is required'}, status=400)
        try:
            contact = User.objects.get(id=contact_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=404)
        qs = MutedChat.objects.filter(user=request.user, contact=contact)
        if qs.exists():
            qs.delete()
            return Response({'detail': 'Unmuted'}, status=200)
        return Response({'detail': 'Not muted'}, status=404)


@login_required
def ticket_detail(request, ticket_id):
    """Display ticket details with comments"""
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    # Check if user can view this ticket
    if not can_view_ticket(request.user, ticket):
        messages.error(request, "You don't have permission to view this ticket.")
        return redirect('ticket_list')
    
    # Get comments based on user role
    if request.user.is_staff or hasattr(request.user, 'userprofile') and getattr(request.user.userprofile.role, 'name', '').lower() in ['admin', 'superadmin']:
        # Staff can see all comments
        comments = ticket.comments.all().select_related('author')
    else:
        # Regular users can see non-internal comments and their own
        comments = ticket.comments.filter(
            models.Q(is_internal=False) | models.Q(author=request.user)
        ).select_related('author')
    
    context = {
        'ticket': ticket,
        'comments': comments,
        'user': request.user,
    }
    return render(request, 'ticket_detail.html', context)


def can_view_ticket(user, ticket):
    """Check if user can view the ticket"""
    # Ticket creator can always view
    if ticket.created_by == user:
        return True
    
    # Assigned user can view
    if ticket.assigned_to == user:
        return True
    
    # Staff can view all tickets
    if user.is_staff:
        return True
    
    return False


class TicketCommentListCreateView(APIView):
    """API view to list and create ticket comments"""
    permission_classes = [IsAuthenticated]

    def get(self, request, ticket_id):
        """Get all comments for a ticket"""
        try:
            ticket = get_object_or_404(Ticket, id=ticket_id)
            
            # Check if user can view this ticket
            if not self.can_view_ticket(request.user, ticket):
                return Response({'detail': 'Permission denied'}, status=403)
            
            # Get comments based on user role
            if request.user.is_staff or hasattr(request.user, 'userprofile') and getattr(request.user.userprofile.role, 'name', '').lower() in ['admin', 'superadmin']:
                # Staff can see all comments
                comments = ticket.comments.all().select_related('author')
            else:
                # Regular users can see non-internal comments and their own
                comments = ticket.comments.filter(
                    models.Q(is_internal=False) | models.Q(author=request.user)
                ).select_related('author')
            
            serializer = TicketCommentSerializer(comments, many=True)
            return Response({
                'success': True,
                'comments': serializer.data
            })
            
        except Exception as e:
            return Response({'detail': str(e)}, status=500)

    def post(self, request, ticket_id):
        """Create a new comment on a ticket"""
        try:
            ticket = get_object_or_404(Ticket, id=ticket_id)
            
            # Check if user can comment on this ticket
            if not self.can_comment_on_ticket(request.user, ticket):
                return Response({'detail': 'Permission denied'}, status=403)
            
            content = request.data.get('content', '').strip()
            is_internal = request.data.get('is_internal', False)
            
            if not content:
                return Response({'detail': 'Content is required'}, status=400)
            
            # Only staff can create internal comments
            if is_internal and not request.user.is_staff:
                return Response({'detail': 'Only staff can create internal comments'}, status=403)
            
            comment = TicketComment.objects.create(
                ticket=ticket,
                author=request.user,
                content=content,
                is_internal=is_internal
            )
            
            serializer = TicketCommentSerializer(comment)
            return Response({
                'success': True,
                'comment': serializer.data
            }, status=201)
            
        except Exception as e:
            return Response({'detail': str(e)}, status=500)

    def can_view_ticket(self, user, ticket):
        """Check if user can view the ticket"""
        # Ticket creator can always view
        if ticket.created_by == user:
            return True
        
        # Assigned user can view
        if ticket.assigned_to == user:
            return True
        
        # Staff can view all tickets
        if user.is_staff:
            return True
        
        return False

    def can_comment_on_ticket(self, user, ticket):
        """Check if user can comment on the ticket"""
        # Ticket creator can always comment
        if ticket.created_by == user:
            return True
        
        # Assigned user can comment
        if ticket.assigned_to == user:
            return True
        
        # Staff can comment on all tickets
        if user.is_staff:
            return True
        
        return False


class TicketCommentDetailView(APIView):
    """API view to update and delete ticket comments"""
    permission_classes = [IsAuthenticated]

    def put(self, request, ticket_id, comment_id):
        """Update a comment"""
        try:
            comment = get_object_or_404(TicketComment, id=comment_id, ticket_id=ticket_id)
            
            # Check permissions
            if not self.can_edit_comment(request.user, comment):
                return Response({'detail': 'Permission denied'}, status=403)
            
            content = request.data.get('content', '').strip()
            if not content:
                return Response({'detail': 'Content is required'}, status=400)
            
            comment.content = content
            comment.save()
            
            serializer = TicketCommentSerializer(comment)
            return Response({
                'success': True,
                'comment': serializer.data
            })
            
        except Exception as e:
            return Response({'detail': str(e)}, status=500)

    def delete(self, request, ticket_id, comment_id):
        """Delete a comment"""
        try:
            comment = get_object_or_404(TicketComment, id=comment_id, ticket_id=ticket_id)
            
            # Check permissions
            if not self.can_delete_comment(request.user, comment):
                return Response({'detail': 'Permission denied'}, status=403)
            
            comment.delete()
            return Response({
                'success': True,
                'message': 'Comment deleted successfully'
            })
            
        except Exception as e:
            return Response({'detail': str(e)}, status=500)

    def can_edit_comment(self, user, comment):
        """Check if user can edit the comment"""
        # Comment author can edit within 5 minutes
        if comment.author == user and comment.can_edit:
            return True
        
        # Staff can edit any comment
        if user.is_staff:
            return True
        
        return False

    def can_delete_comment(self, user, comment):
        """Check if user can delete the comment"""
        # Comment author can delete
        if comment.author == user:
            return True
        
        # Staff can delete any comment
        if user.is_staff:
            return True
        
        return False
