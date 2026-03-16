"""
Signals for payments app
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from superadmin.models import Payment, Subscription


@receiver(post_save, sender=Payment)
def payment_created(sender, instance, created, **kwargs):
    """
    Handle payment creation and update subscription status
    """
    if created and instance.status == 'completed':
        subscription = instance.subscription
        
        # Only process if subscription is linked
        if subscription:
            # Update subscription to active
            subscription.status = 'active'
            subscription.save()
            
            # Update company subscription status
            company = subscription.company
            company.subscription_status = 'active'
            company.save()
            
            # Log the payment completion
            print(f"Payment {instance.transaction_id} completed - Subscription {subscription.id} activated")
        else:
            # Payment created without subscription link
            print(f"Payment {instance.transaction_id} created without subscription link")


@receiver(post_save, sender=Payment)
def payment_status_changed(sender, instance, **kwargs):
    """
    Handle payment status changes
    """
    try:
        # Get the old status from database
        old_payment = Payment.objects.get(id=instance.id)
        old_status = old_payment.status
        
        # Check if status changed
        if old_status != instance.status:
            if instance.status == 'completed':
                # Activate subscription
                subscription = instance.subscription
                if subscription:
                    subscription.status = 'active'
                    subscription.save()
                    
                    company = subscription.company
                    company.subscription_status = 'active'
                    company.save()
                    
                    print(f"Payment {instance.transaction_id} marked as completed")
                else:
                    print(f"Payment {instance.transaction_id} completed but no subscription linked")
                
            elif instance.status == 'failed':
                # Handle failed payment
                print(f"Payment {instance.transaction_id} failed")
                
            elif instance.status == 'refunded':
                # Handle refund
                print(f"Payment {instance.transaction_id} refunded")
                
    except Payment.DoesNotExist:
        # New payment, no old status to compare
        pass
