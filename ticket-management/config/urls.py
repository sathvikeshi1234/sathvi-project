"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.views.generic import TemplateView
from dashboards.views import ticket_dashboard_page
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', TemplateView.as_view(template_name='landingpage/index.html'), name='home'),
    path('test-password/', TemplateView.as_view(template_name='test_password.html'), name='test_password'),
    path('ticket-dashboard/<str:page>/', ticket_dashboard_page, name='ticket_dashboard_page'),
    path('ticket-dashboard/', TemplateView.as_view(template_name='admindashboard/index.html'), name='ticket_dashboard'),
    path('admin/', admin.site.urls),
    path('api/', include(('api.urls', 'api'), namespace='api')),
    path("", include(('users.urls', 'users'), namespace='users')),   
    path("dashboard/", include(('dashboards.urls', 'dashboards'), namespace='dashboards')),
    path("tickets/", include(("tickets.urls", 'tickets'), namespace='tickets')),
    path('superadmin/', include(('superadmin.urls', 'superadmin'), namespace='superadmin')),
    path('payments/', include(('payments.urls', 'payments'), namespace='payments')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
