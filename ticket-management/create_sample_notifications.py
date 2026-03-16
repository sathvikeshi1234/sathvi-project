#!/usr/bin/env python
import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from superadmin.models import Notification

def create_sample_notifications():
    """Create sample notifications for testing"""
    
    # Get a superadmin user
    try:
        superadmin = User.objects.filter(is_superuser=True).first()
        if not superadmin:
            print("No superadmin user found. Please create one first.")
            return
        print(f"Using superadmin user: {superadmin.username}")
    except Exception as e:
        print(f"Error getting superadmin user: {e}")
        return
    
    # Create sample notifications
    notifications_data = [
        {
            'title': 'New User Registration',
            'message': 'John Doe registered as Admin user from New York',
            'notification_type': 'user',
            'priority': 'medium',
            'user': superadmin
        },
        {
            'title': 'Payment Received',
            'message': 'Tech Corp paid ₹1,999 for Standard plan subscription',
            'notification_type': 'payment',
            'priority': 'medium',
            'user': superadmin
        },
        {
            'title': 'System Update',
            'message': 'System maintenance completed successfully',
            'notification_type': 'system',
            'priority': 'low',
            'user': superadmin
        },
        {
            'title': 'High Priority Ticket',
            'message': 'Critical issue reported by ABC Company - Server down',
            'notification_type': 'error',
            'priority': 'high',
            'user': superadmin
        },
        {
            'title': 'Weekly Report Available',
            'message': 'Your weekly analytics report is ready for download',
            'notification_type': 'info',
            'priority': 'low',
            'user': superadmin
        }
    ]
    
    created_count = 0
    for notif_data in notifications_data:
        notification = Notification.create_notification(**notif_data)
        created_count += 1
        print(f"Created notification: {notification.title}")
    
    print(f"\nSuccessfully created {created_count} sample notifications!")

if __name__ == '__main__':
    create_sample_notifications()
