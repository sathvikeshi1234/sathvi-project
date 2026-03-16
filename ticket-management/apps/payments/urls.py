"""
URLs for the payments app
"""

from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Payment creation and processing
    path('create/', views.payment_create, name='payment_create'),
    path('process/<int:subscription_id>/', views.payment_process, name='payment_process'),
    
    # Payment viewing and management
    path('detail/<int:payment_id>/', views.payment_detail, name='payment_detail'),
    path('list/', views.payments_list, name='payments_list'),
    path('update-status/<int:payment_id>/', views.payment_update_status, name='payment_update_status'),
    
    # Subscription payments
    path('subscription/<int:subscription_id>/', views.subscription_payments, name='subscription_payments'),
    
    # Receipts and documents
    path('receipt/<int:payment_id>/', views.payment_receipt, name='payment_receipt'),
    
    # Webhooks (for payment gateway integration)
    path('webhook/', views.payment_webhook, name='payment_webhook'),
    
    # Razorpay Payment Gateway
    path('razorpay/create-order/', views.razorpay_create_order, name='razorpay_create_order'),
    path('razorpay/verify/', views.razorpay_verify_payment, name='razorpay_verify_payment'),
    path('razorpay/webhook/', views.razorpay_webhook, name='razorpay_webhook'),
]
