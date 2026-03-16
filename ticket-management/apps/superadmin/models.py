from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone
from datetime import timedelta

# Create your models here.
class Plan(models.Model):
    BILLING_CHOICES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    billing_cycle = models.CharField(max_length=10, choices=BILLING_CHOICES, default='monthly')
    users = models.PositiveIntegerField()
    storage = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active')
    created_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} - ${self.price}/{self.billing_cycle}"
class Company(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True, null=True)
    
    # Plan and subscription fields
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True)
    plan_expiry_date = models.DateField(null=True, blank=True)
    subscription_status = models.CharField(
        max_length=20, 
        choices=[
            ('active', 'Active'),
            ('expired', 'Expired'),
            ('trial', 'Trial'),
            ('cancelled', 'Cancelled')
        ], 
        default='trial'
    )
    subscription_start_date = models.DateField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Users relationship
    users = models.ManyToManyField('users.UserProfile', blank=True, related_name='companies')

    def __str__(self):
        return self.name
    
    def has_admin_or_superadmin_user(self):
        """Check if this company has any Admin or SuperAdmin users"""
        from users.models import UserProfile
        from users.models import Role
        
        admin_role = Role.objects.filter(name__in=['Admin', 'SuperAdmin'])
        if admin_role.exists():
            return UserProfile.objects.filter(
                role__in=admin_role
            ).exists()
        return False





class SuperAdminSettings(models.Model):
    """Dynamic settings model for superadmin"""
    
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('es', 'Spanish'),
        ('fr', 'French'),
        ('de', 'German'),
        ('zh', 'Chinese'),
        ('ja', 'Japanese'),
    ]
    
    TIMEZONE_CHOICES = [
        ('UTC', 'UTC'),
        ('EST', 'Eastern Time'),
        ('PST', 'Pacific Time'),
        ('IST', 'India Standard Time'),
        ('CET', 'Central European Time'),
        ('JST', 'Japan Standard Time'),
    ]
    
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar ($)'),
        ('EUR', 'Euro (€)'),
        ('GBP', 'British Pound (£)'),
        ('JPY', 'Japanese Yen (¥)'),
        ('INR', 'Indian Rupee (₹)'),
    ]
    
    # User Settings
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    profile_name = models.CharField(max_length=100, blank=True)
    profile_email = models.EmailField(blank=True)
    profile_phone = models.CharField(max_length=20, blank=True)
    profile_address = models.TextField(blank=True)
    
    # Professional Information
    department = models.CharField(max_length=100, blank=True)
    role = models.CharField(max_length=100, blank=True)
    employee_id = models.CharField(max_length=20, blank=True)
    join_date = models.DateField(null=True, blank=True)
    skills = models.TextField(blank=True)
    
    # Notification Settings
    email_notifications = models.BooleanField(default=True)
    in_app_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=False)
    
    # Security Settings
    two_factor_enabled = models.BooleanField(default=False)
    profile_visibility = models.CharField(
        max_length=20,
        choices=[('public', 'Public'), ('private', 'Private'), ('team', 'Team Only')],
        default='public'
    )
    
    # App Settings
    dark_mode = models.BooleanField(default=False)
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='en')
    timezone = models.CharField(max_length=10, choices=TIMEZONE_CHOICES, default='UTC')
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='INR')
    
    # System Settings
    maintenance_mode = models.BooleanField(default=False)
    user_registration = models.BooleanField(default=True)
    email_verification = models.BooleanField(default=True)
    remember_me = models.BooleanField(default=True)
    show_tutorial = models.BooleanField(default=True)
    
    # Ticket Settings
    default_ticket_status = models.CharField(max_length=50, default='Open')
    default_ticket_priority = models.CharField(max_length=20, default='Medium')
    auto_ticket_assignment = models.BooleanField(default=True)
    allow_ticket_reopen = models.BooleanField(default=True)
    first_response_hours = models.IntegerField(default=24)
    resolution_time_hours = models.IntegerField(default=72)
    sla_business_hours = models.CharField(max_length=100, default='Business Hours (9 AM - 5 PM, Mon-Fri)')
    
    # UI Settings
    theme = models.CharField(max_length=10, default='light')
    primary_color = models.CharField(max_length=7, default='#0d6efd')
    fixed_header = models.BooleanField(default=True)
    fixed_sidebar = models.BooleanField(default=True)
    collapsed_sidebar = models.BooleanField(default=False)
    
    # Company Settings
    company_name = models.CharField(max_length=200, blank=True, default="")
    website_url = models.URLField(blank=True, default="")
    contact_email = models.EmailField(blank=True, default="")
    contact_phone = models.CharField(max_length=50, blank=True, default="")
    address = models.TextField(blank=True, default="")
    company_logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    collapsed_logo = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Settings for {self.user.username}"
    
    def get_currency_symbol_display(self):
        """Return currency symbol based on currency code"""
        currency_symbols = {
            'USD': '$',
            'EUR': '€',
            'GBP': '£',
            'JPY': '¥',
            'INR': '₹',
        }
        return currency_symbols.get(self.currency, '₹')  # Default to INR
    
    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class NotificationTemplate(models.Model):
    """Email notification templates"""
    
    name = models.CharField(max_length=100)
    subject = models.CharField(max_length=200)
    html_content = models.TextField()
    text_content = models.TextField(blank=True)
    variables = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name


class Subscription(models.Model):
    """Subscription model for companies"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
        ('suspended', 'Suspended'),
        ('trial', 'Trial'),
    ]
    
    BILLING_CYCLE_CHOICES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='subscriptions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    billing_cycle = models.CharField(max_length=10, choices=BILLING_CYCLE_CHOICES, default='monthly')
    
    # Dates
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    next_billing_date = models.DateField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    # Pricing
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Additional fields
    auto_renew = models.BooleanField(default=True)
    trial_end_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # Calculate total amount
        from decimal import Decimal
        # Ensure all values are Decimal for proper arithmetic
        base_price = Decimal(str(self.base_price)) if self.base_price else Decimal('0.00')
        discount_amount = Decimal(str(self.discount_amount)) if self.discount_amount else Decimal('0.00')
        tax_amount = Decimal(str(self.tax_amount)) if self.tax_amount else Decimal('0.00')
        self.total_amount = base_price - discount_amount + tax_amount
        
        # Set next billing date if not set
        if not self.next_billing_date and self.start_date:
            self.calculate_next_billing_date()
        
        # Check if this is a new subscription
        is_new = self.pk is None
        
        super().save(*args, **kwargs)
        
        # Create automatic payment for new active subscriptions
        if is_new and self.status == 'active':
            self.create_initial_payment()
    
    def calculate_next_billing_date(self):
        """Calculate next billing date based on billing cycle and current date"""
        from django.utils import timezone
        from datetime import timedelta
        
        current_date = timezone.now().date()
        
        if self.billing_cycle == 'monthly':
            # Add 30 days to current date or start date
            if self.next_billing_date and self.next_billing_date > current_date:
                # Update from existing next billing date
                self.next_billing_date = self.next_billing_date + timedelta(days=30)
            else:
                # Calculate from current date
                self.next_billing_date = current_date + timedelta(days=30)
        else:  # yearly
            # Add 365 days to current date or start date
            if self.next_billing_date and self.next_billing_date > current_date:
                # Update from existing next billing date
                self.next_billing_date = self.next_billing_date + timedelta(days=365)
            else:
                # Calculate from current date
                self.next_billing_date = current_date + timedelta(days=365)
    
    def update_next_billing_date(self):
        """Update next billing date and save"""
        self.calculate_next_billing_date()
        self.save(update_fields=['next_billing_date'])
    
    @property
    def is_billing_due(self):
        """Check if billing is due (within 7 days)"""
        from django.utils import timezone
        from datetime import timedelta
        
        current_date = timezone.now().date()
        due_date = self.next_billing_date - timedelta(days=7)
        return current_date >= due_date and self.status == 'active'
    
    @property
    def days_until_billing(self):
        """Days until next billing date"""
        from django.utils import timezone
        
        if self.status != 'active' or not self.next_billing_date:
            return 0
            
        current_date = timezone.now().date()
        delta = self.next_billing_date - current_date
        return delta.days if delta.days > 0 else 0
    
    def __str__(self):
        return f"{self.company.name} - {self.plan.name} ({self.status})"
    
    @property
    def is_expired(self):
        from django.utils import timezone
        return timezone.now().date() > self.end_date
    
    @property
    def days_until_expiry(self):
        from django.utils import timezone
        delta = self.end_date - timezone.now().date()
        return delta.days if delta.days > 0 else 0
    
    @property
    def is_trial_active(self):
        """Check if the subscription is in trial period"""
        from django.utils import timezone
        if self.status != 'trial':
            return False
        
        # Check if within trial period (using end_date)
        return timezone.now().date() <= self.end_date
    
    @property
    def trial_days_remaining(self):
        """Days remaining in trial period"""
        from django.utils import timezone
        if self.status != 'trial':
            return 0
        
        delta = self.end_date - timezone.now().date()
        return delta.days if delta.days > 0 else 0
    
    @property
    def is_payment_required(self):
        """Check if payment is required to continue service"""
        from django.utils import timezone
        
        if self.status == 'trial':
            # Payment required after trial expires
            return timezone.now().date() > self.end_date
        elif self.status == 'expired':
            return True
        elif self.status == 'active':
            # Check if next billing date is past
            return self.next_billing_date and timezone.now().date() > self.next_billing_date
        
        return False
    
    def can_access_dashboard(self, user=None):
        """Check if user can access dashboard based on subscription status and role"""
        from django.utils import timezone
        
        if self.status == 'active':
            # Active subscriptions always have access for all roles
            return True
        elif self.status == 'trial':
            # Trial users have access during trial period ONLY if they are Admin or SuperAdmin
            if self.is_trial_active and user:
                return self.is_user_admin_or_superadmin(user)
            return False
        elif self.status == 'expired' or self.status == 'cancelled':
            # No access for expired or cancelled subscriptions
            return False
        
        return False
    
    def is_user_admin_or_superadmin(self, user):
        """Check if a specific user is Admin or SuperAdmin"""
        try:
            user_profile = user.userprofile
            user_role = user_profile.role.name if user_profile.role else None
            return user_role in ['Admin', 'SuperAdmin']
        except AttributeError:
            return False
    
    def is_trial_for_admin_only(self):
        """Check if trial access should be granted (Admin/SuperAdmin only)"""
        # This method is kept for backward compatibility
        # Check if there are admin users in the system
        return self.company.has_admin_or_superadmin_user()
    
    def expire_trial_if_needed(self):
        """Expire trial if 30 days have passed"""
        from django.utils import timezone
        
        if self.status == 'trial':
            trial_end = self.start_date + timedelta(days=30)
            if timezone.now().date() > trial_end:
                self.status = 'expired'
                self.save()
                return True
        return False
    
    def activate_subscription_after_payment(self):
        """Activate subscription after successful payment"""
        from django.utils import timezone
        from datetime import timedelta
        
        self.status = 'active'
        
        # Set new billing dates
        if not self.start_date:
            self.start_date = timezone.now().date()
        
        # Calculate end date based on billing cycle
        if self.billing_cycle == 'monthly':
            self.end_date = self.start_date + timedelta(days=30)
            self.next_billing_date = timezone.now().date() + timedelta(days=30)
        else:  # yearly
            self.end_date = self.start_date + timedelta(days=365)
            self.next_billing_date = timezone.now().date() + timedelta(days=365)
        
        self.save()
    
    def create_initial_payment(self):
        """Create initial payment when subscription is created"""
        from django.utils import timezone
        
        # Only create payment for active subscriptions, not trials
        if self.status == 'active':
            Payment.objects.create(
                subscription=self,
                company=self.company,
                amount=self.total_amount,
                payment_method='bank_transfer',  # Default payment method
                payment_type='subscription',
                status='completed',  # Auto-complete initial payment
                payment_date=timezone.now(),
                transaction_id=f'SUB-{self.id}-{timezone.now().strftime("%Y%m%d")}',
                invoice_number=f'INV-{self.id}-{timezone.now().strftime("%Y%m%d")}',
                notes=f'Initial payment for {self.plan.name} subscription'
            )


class Payment(models.Model):
    """Payment model for subscription payments"""
    
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('paypal', 'PayPal'),
        ('stripe', 'Stripe'),
        ('razorpay', 'Razorpay'),
        ('check', 'Check'),
        ('cash', 'Cash'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_TYPE_CHOICES = [
        ('subscription', 'Subscription'),
        ('setup_fee', 'Setup Fee'),
        ('upgrade', 'Upgrade'),
        ('refund', 'Refund'),
        ('credit', 'Credit'),
        ('penalty', 'Penalty'),
    ]
    
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='payments')
    
    # Payment details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, default='subscription')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Transaction details
    transaction_id = models.CharField(max_length=100, blank=True)
    invoice_number = models.CharField(max_length=50, blank=True)
    payment_date = models.DateTimeField()
    
    # Gateway details
    gateway_response = models.JSONField(default=dict, blank=True)
    gateway_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Refund details
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    refund_reason = models.TextField(blank=True)
    refunded_at = models.DateTimeField(null=True, blank=True)
    
    # Additional fields
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Payment #{self.id} - {self.company.name} - ${self.amount}"
    
    @property
    def net_amount(self):
        return self.amount - self.gateway_fee - self.refund_amount
    
    def get_payment_type_display(self):
        """Return human-readable payment type"""
        choices = dict(self.PAYMENT_TYPE_CHOICES)
        return choices.get(self.payment_type, self.payment_type.title())
    
    def get_payment_method_display(self):
        """Return human-readable payment method"""
        choices = dict(self.PAYMENT_METHOD_CHOICES)
        return choices.get(self.payment_method, self.payment_method.title())
    
    def get_status_display(self):
        """Return human-readable status"""
        choices = dict(self.PAYMENT_STATUS_CHOICES)
        return choices.get(self.status, self.status.title())


class SubscriptionMetrics(models.Model):
    """Subscription metrics for analytics"""
    
    date = models.DateField()
    active_subscriptions = models.PositiveIntegerField(default=0)
    new_subscriptions = models.PositiveIntegerField(default=0)
    cancelled_subscriptions = models.PositiveIntegerField(default=0)
    churn_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    monthly_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    mrr = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Monthly Recurring Revenue
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"Metrics for {self.date}"


class Notification(models.Model):
    """Notification model for SuperAdmin dashboard"""
    
    TYPE_CHOICES = [
        ('info', 'Information'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('system', 'System'),
        ('payment', 'Payment'),
        ('subscription', 'Subscription'),
        ('user', 'User Management'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='info')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    # Target user (null means broadcast to all superadmins)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    
    # Action URL (optional)
    action_url = models.URLField(max_length=500, blank=True, null=True)
    action_text = models.CharField(max_length=50, blank=True, null=True)
    
    # Status and tracking
    is_read = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Auto-expiry (optional)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', 'created_at']),
            models.Index(fields=['notification_type', 'priority']),
            models.Index(fields=['is_active', 'expires_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.username if self.user else 'Broadcast'}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    def is_expired(self):
        """Check if notification has expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    @classmethod
    def create_notification(cls, title, message, notification_type='info', priority='medium', 
                          user=None, action_url=None, action_text=None, expires_in_hours=None):
        """Create a new notification"""
        expires_at = None
        if expires_in_hours:
            expires_at = timezone.now() + timezone.timedelta(hours=expires_in_hours)
        
        return cls.objects.create(
            title=title,
            message=message,
            notification_type=notification_type,
            priority=priority,
            user=user,
            action_url=action_url,
            action_text=action_text,
            expires_at=expires_at
        )
    
    @classmethod
    def get_user_notifications(cls, user, unread_only=False):
        """Get notifications for a specific user"""
        queryset = cls.objects.filter(
            models.Q(user=user) | models.Q(user__isnull=True),  # User-specific or broadcast
            is_active=True
        ).exclude(
            expires_at__lt=timezone.now()  # Exclude expired
        )
        
        if unread_only:
            queryset = queryset.filter(is_read=False)
        
        return queryset.order_by('-created_at')
    
    @classmethod
    def get_unread_count(cls, user):
        """Get count of unread notifications for user"""
        return cls.get_user_notifications(user, unread_only=True).count()
