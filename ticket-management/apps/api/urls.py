from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('admin-users/', views.admin_users_api, name='admin_users_api'),
    path('customers/', views.customers_api, name='customers_api'),
    path('users/<int:user_id>/', views.user_detail_api, name='user_detail_api'),
    path('users/<int:user_id>/set-password/', views.set_password_api, name='set_password_api'),
]
