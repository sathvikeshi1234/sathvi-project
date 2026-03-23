from django.urls import path
from . import views

app_name = "dashboards"

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),

    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/payment/', views.admin_payment_page, name='admin_payment_page'),
    path('admin-dashboard/api/notifications/', views.admin_notifications_api, name='admin_notifications_api'),
    path('admin-dashboard/reports/export/<str:export_format>/', views.admin_reports_export, name='admin_reports_export'),
    path('admin-dashboard/ticket/<str:identifier>/', views.admin_ticket_detail, name='admin_ticket_detail'),
    path('admin-dashboard/ticket/<str:identifier>/edit/', views.admin_ticket_edit, name='admin_ticket_edit'),
    path('admin-dashboard/<path:page>/', views.admin_dashboard_page, name='admin_dashboard_page'),

    path('agent-dashboard/', views.agent_dashboard, name='agent_dashboard'),
    path('agent-dashboard/index.html', views.agent_dashboard, name='agent_dashboard_index'),
    path('agent-dashboard/api/notifications/', views.agent_notifications_api, name='agent_notifications_api'),
    path('agent-dashboard/ticket/<str:identifier>/', views.agent_ticket_detail, name='agent_ticket_detail'),
    path('agent-dashboard/<path:page>.html', views.agent_dashboard_page, name='agent_dashboard_page'),
    path('agent-dashboard/<path:page>', views.agent_dashboard_page, name='agent_dashboard_page_partial'),

    path('user-dashboard/', views.user_dashboard, name='user_dashboard'),
    path('user-dashboard/ticket/<str:identifier>/', views.user_ticket_detail, name='user_ticket_detail'),
    path('user-dashboard/ticket/<str:identifier>/edit/', views.user_ticket_edit, name='user_ticket_edit'),
    path('user-dashboard/ticket/<str:identifier>/rate/', views.user_ticket_rate, name='user_ticket_rate'),
    path('user-dashboard/ticket/<str:identifier>/delete/', views.user_ticket_delete, name='user_ticket_delete'),
    path('user-dashboard/api/notifications/', views.user_notifications_api, name='user_notifications_api'),
    path('user-dashboard/clear-payment-modal/', views.clear_payment_modal, name='clear_payment_modal'),
    path('user-dashboard/record-payment-transaction/', views.record_payment_transaction, name='record_payment_transaction'),
    path('user-dashboard/faq/search/', views.faq_search_api, name='faq_search_api'),
    path('user-dashboard/<str:page>/', views.user_dashboard_page, name='user_dashboard_page'),

    path('api/site-settings/', views.SiteSettingsView.as_view(), name='site_settings_api'),
    path('test-edit/', views.test_edit_page, name='test_edit_page'),
]