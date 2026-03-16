"""
URL configuration for core app
"""

from django.urls import path, include
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('payment/', views.payment_modal, name='payment_modal'),
    path('api/start-trial/', views.start_trial, name='start_trial'),
    path('api/process-payment/', views.process_payment, name='process_payment'),
    path('api/payment-status/', views.check_payment_status, name='check_payment_status'),
    path('tickets/', include('tickets.urls', namespace='tickets')),
]
