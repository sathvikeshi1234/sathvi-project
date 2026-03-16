from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from superadmin.models import Company, Plan, Subscription
from django.utils import timezone
from datetime import timedelta

@receiver(post_migrate)
def create_default_roles(sender, **kwargs):
    if sender.name == 'users':
        # Import here to avoid circular import
        from .models import Role
        roles = ['Admin', 'Agent', 'User']
        for role_name in roles:
            Role.objects.get_or_create(name=role_name)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Import here to avoid circular import
        from .models import Role, UserProfile
        role, _ = Role.objects.get_or_create(name='User')
        UserProfile.objects.create(user=instance, role=role)


@receiver(post_save, sender=Company)
def create_trial_subscription(sender, instance, created, **kwargs):
    """
    Automatically create a free trial subscription for new companies
    """
    from django.conf import settings
    
    if created and getattr(settings, 'FREE_TRIAL_AUTO_ASSIGN', True):
        # Get the default/free plan from settings
        plan_name = getattr(settings, 'FREE_TRIAL_PLAN_NAME', 'Basic')
        default_plan = Plan.objects.filter(name__icontains=plan_name).first()
        if not default_plan:
            default_plan = Plan.objects.first()
        
        if default_plan:
            # Get trial duration from settings
            trial_days = getattr(settings, 'FREE_TRIAL_DURATION_DAYS', 30)
            
            # Create trial subscription
            trial_start = timezone.now().date()
            trial_end = trial_start + timedelta(days=trial_days)
            
            subscription = Subscription.objects.create(
                company=instance,
                plan=default_plan,
                status='trial',
                billing_cycle='monthly',
                start_date=trial_start,
                end_date=trial_end,
                next_billing_date=trial_end,
                base_price=0,  # Free trial
                discount_amount=0,
                tax_amount=0,
                total_amount=0,
                auto_renew=False  # Don't auto-renew from trial
            )
            
            # Update company subscription status
            instance.subscription_status = 'trial'
            instance.plan = default_plan
            instance.plan_expiry_date = trial_end
            instance.subscription_start_date = trial_start
            instance.save()
            
            print(f"Created {trial_days}-day trial subscription for company: {instance.name}")
        else:
            print(f"No plan available for trial subscription for company: {instance.name}")