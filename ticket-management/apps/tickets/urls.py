from django.urls import path
from . import views
from .views import DashboardStatsView, RecentTicketsView, TicketListCreateView, TicketStatusUpdateView, MutedChatView, TicketCommentListCreateView, TicketCommentDetailView 

urlpatterns = [
    path("", views.ticket_list, name="ticket_list"),
    path("create/", views.ticket_create, name="ticket_create"),
    path("<int:pk>/", views.ticket_detail, name="ticket_detail"),
    path("<int:pk>/edit/", views.ticket_edit, name="ticket_edit"),
    path("<int:pk>/delete/", views.ticket_delete, name="ticket_delete"),
    
    # Comment API endpoints
    path("<int:ticket_id>/comments/", TicketCommentListCreateView.as_view(), name="api-ticket-comments"),
    path("<int:ticket_id>/comments/<int:comment_id>/", TicketCommentDetailView.as_view(), name="api-ticket-comment-detail"),
    
    # Dashboard API endpoints
    path("dashboard/stats/", DashboardStatsView.as_view(), name="dashboard-stats"),
    path("dashboard/recent-tickets/", RecentTicketsView.as_view(), name="recent-tickets"),
    path("api/tickets/", TicketListCreateView.as_view(), name="api-tickets"),
    path("api/tickets/<int:pk>/status/", TicketStatusUpdateView.as_view(), name="api-ticket-status"),
    path("api/chat/mute/", MutedChatView.as_view(), name="api-chat-mute"),
]
