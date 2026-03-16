from django.urls import path

from . import views

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import RegisterView, AgentsListView, CustomersListView, RolesListView, RoleDetailView, ChatMessagesView, UserDetailView, ChatThreadDetailView, UsersListView, SetUserPasswordView, AgentLoginAPIView



urlpatterns = [

    path("login/", views.login_view, name="login"),

    path('signup/', views.signup_view, name='signup'),

    path('agent-signup/', views.agent_signup_view, name='agent_signup'),

    path('forgot-password/', views.forgot_password_view, name='forgot_password'),

    path('forgot-password/code/', views.forgot_password_code_view, name='forgot_password_code'),

    path('forgot-password/new-password/', views.forgot_password_new_password_view, name='forgot_password_new_password'),

    path('reset/<uidb64>/<token>/', views.reset_password, name='reset_password'),

    path("logout/", views.logout_view, name="logout"),

    # Separate admin/user auth routes

    path('admin-login/', views.admin_login_view, name='admin_login'),

    path('agent-login/', views.agent_login_view, name='agent_login'),

    path('user-login/', views.user_login_view, name='user_login'),

    path('admin-signup/', views.admin_signup_view, name='admin_signup'),

    path('user-signup/', views.user_signup_view, name='user_signup'),

]



urlpatterns += [

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('api/register/', RegisterView.as_view(), name='register'),

    path('api/agents/', AgentsListView.as_view(), name='api_agents'),

    path('api/customers/', CustomersListView.as_view(), name='api_customers'),

    path('api/users/', UsersListView.as_view(), name='api_users'),

    path('api/users/<int:user_id>/', UserDetailView.as_view(), name='api_user_detail'),

    path('api/roles/', RolesListView.as_view(), name='api_roles'),

    path('api/roles/<int:role_id>/', RoleDetailView.as_view(), name='api_role_detail'),

    path('api/chat/messages/', ChatMessagesView.as_view(), name='api_chat_messages'),

    path('api/chat/thread/<int:contact_id>/', ChatThreadDetailView.as_view(), name='api_chat_thread'),

    path('api/users/<int:user_id>/set-password/', SetUserPasswordView.as_view(), name='api_set_user_password'),

    path('api/agent/login/', AgentLoginAPIView.as_view(), name='api_agent_login'),

]