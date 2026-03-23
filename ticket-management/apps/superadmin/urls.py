from django.urls import path



from .import views



from .views import superadmin_login, admin_login, superadmin_logout, companies_list, company_create, company_detail, company_edit, company_delete, subscriptions_list, subscription_view, users_list, agents_list, create_user, recent_comments_api, ticket_search_api, get_notifications_api, superadmin_signup, plan_edit, plan_add, transaction_details, mark_notification_read, delete_notification, mark_all_notifications_read, payment_create, subscription_change_plan, subscription_renew, admin_management, add_admin



app_name = "superadmin" 







urlpatterns = [



    path('login/', superadmin_login, name='superadmin_login'),



    # path('admin-login/', admin_login, name='admin_login'),



    # path('admin-signup/', admin_signup, name='admin_signup'),



    path('signup/', superadmin_signup, name='superadmin_signup'),



    path("dashboard/", views.superadmin_dashboard, name="superadmin_dashboard"),



    



    path('logout/', superadmin_logout, name='superadmin_logout'),



    path('plans/', views.plan_list, name='plans_list'),
    path('plans/add/', plan_add, name='plan_add'),
    path('plans/<int:plan_id>/edit/', plan_edit, name='plan_edit'),


    # path('plans/plans-add.html', views.plans_add_legacy, name='plans_add_legacy'),


    # path('plans/<int:plan_id>/edit/', views.plan_edit, name='superadmin_plan_edit'),  # Commented out - function doesn't exist



    path("companies/", companies_list, name="companies_list"),
    path("companies/add/", company_create, name="company_add"),
    path("companies/create/", company_create, name="company_create"),


    # path("companies/api/", views.companies_api, name="companies_api"),


    path("companies/<int:company_id>/edit/", views.company_edit, name="company_edit"),


    path("companies/<int:company_id>/detail/", views.company_detail, name="company_detail"),
    path("companies/<int:company_id>/delete/", views.company_delete, name="company_delete"),



    path("users/", users_list, name="users_list"),
    path("users/create/", create_user, name="create_user"),
    path("agents/", agents_list, name="agents_list"),
    path("admin-management/", admin_management, name="admin_management"),
    path("admin-management/add/", add_admin, name="add_admin"),



    # path("users/add/", add_user, name="add_user"),



    # path("users/<int:user_id>/profile/", user_profile_view, name="user_profile"),


    # path("users/<int:user_id>/role/", user_role_view, name="user_role"),



    # path("users/<int:user_id>/change-role/", change_user_role, name="change_user_role"),



    path("users/<int:user_id>/toggle-status/", views.toggle_user_status, name="toggle_user_status"),



    path("users/<int:user_id>/view/", views.user_detail, name="user_detail"),
    path("users/<int:user_id>/edit/", views.user_edit, name="user_edit"),
    # path("users/<int:user_id>/reset-password/", views.reset_user_password, name="reset_user_password"),
    # path("users/<int:user_id>/assign-company/", views.assign_user_company, name="assign_user_company"),
    path("users/<int:user_id>/delete/", views.delete_user, name="delete_user"),



    path("subscriptions/", subscriptions_list, name="subscriptions_list"),

    # path("all_subscriptions/", views.superadmin_page, {'page': 'all_subscriptions'}, name='all_subscriptions'),

    # path("subscriptions/create/", subscription_create, name="subscription_create"),



    path("subscriptions/<int:subscription_id>/view/", subscription_view, name="subscription_view"),

    path("subscriptions/<int:subscription_id>/change-plan/", subscription_change_plan, name="subscription_change_plan"),

    path("subscriptions/<int:subscription_id>/renew/", subscription_renew, name="subscription_renew"),



    # path("subscriptions/<int:subscription_id>/edit/", subscription_edit, name="subscription_edit"),



    # path("subscriptions/<int:subscription_id>/suspend/", subscription_suspend, name="subscription_suspend"),



    # path("subscriptions/<int:subscription_id>/payment/", payment_process, name="payment_process"),



    path("payments/create/", payment_create, name="payment_create"),



    # path("subscriptions/bulk-action/", views.bulk_subscription_action, name="bulk_subscription_action"),



    



    # Transaction API URLs



    path("transactions/<int:payment_id>/details/", transaction_details, name="transaction_details"),



    # path("transactions/<int:payment_id>/receipt/", transaction_receipt, name="transaction_receipt"),



    # path("transactions/<int:payment_id>/mark-complete/", transaction_mark_complete, name="transaction_mark_complete"),



    # path("transactions/<int:payment_id>/refund/", transaction_refund, name="transaction_refund"),



    # path("transactions/<int:payment_id>/delete/", transaction_delete, name="transaction_delete"),



    



    # Notification URLs



    path("notifications/api/", get_notifications_api, name="get_notifications_api"),

    path("notifications/<int:notification_id>/mark-read/", mark_notification_read, name="mark_notification_read"),

    path("notifications/<int:notification_id>/delete/", delete_notification, name="delete_notification"),

    path("notifications/mark-all-read/", mark_all_notifications_read, name="mark_all_notifications_read"),

    # path("notifications/create/", create_notification_api, name="create_notification_api"),



    



    # Recent Comments API



    path("comments/recent/", recent_comments_api, name="recent_comments_api"),



    



    # Ticket Search API



    path("tickets/search/", ticket_search_api, name="ticket_search_api"),



    



    path("<str:page>/", views.superadmin_page, name="superadmin_page")



]