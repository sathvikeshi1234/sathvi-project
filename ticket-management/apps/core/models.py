from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid


class Plan(models.Model):
    """
    Subscription plan model with pricing and features
    """
    PLAN_TYPES = [
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
        ('enterprise', 'Enterprise'),
        ('custom', 'Custom'),
    ]
    
    BILLING_CYCLES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annually', 'Annually'),
        ('biennial', 'Biennial'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('draft', 'Draft'),
        ('archived', 'Archived'),
    ]
    
    # Basic Information
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, help_text="URL-friendly version of plan name")
    description = models.TextField(blank=True, help_text="Detailed description of the plan")
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES, default='basic')
    
    # Pricing Information
    price_monthly = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Monthly price in USD"
    )
    price_quarterly = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Quarterly price in USD"
    )
    price_annually = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Annual price in USD"
    )
    price_biennial = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Biennial price in USD"
    )
    
    # Currency and Billing
    currency = models.CharField(max_length=3, default='USD', help_text="Currency code (ISO 4217)")
    billing_cycles = models.CharField(
        max_length=20, 
        choices=BILLING_CYCLES, 
        default='monthly',
        help_text="Available billing cycles for this plan"
    )
    
    # Trial Period
    trial_days = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(365)],
        help_text="Number of trial days (0 = no trial)"
    )
    trial_features = models.JSONField(
        default=dict,
        blank=True,
        help_text="Features available during trial period"
    )
    
    # Limits and Quotas
    max_users = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Maximum number of users allowed (null = unlimited)"
    )
    max_tickets_per_month = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Maximum tickets per month (null = unlimited)"
    )
    max_agents = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Maximum agents allowed (null = unlimited)"
    )
    storage_limit_gb = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Storage limit in GB (null = unlimited)"
    )
    api_calls_per_month = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="API calls allowed per month (null = unlimited)"
    )
    
    # Features and Capabilities
    features = models.JSONField(
        default=dict,
        blank=True,
        help_text="Plan features as key-value pairs"
    )
    
    # Status and Metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_popular = models.BooleanField(default=False, help_text="Mark as popular plan")
    sort_order = models.PositiveIntegerField(default=0, help_text="Order in which plans are displayed")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional metadata as key-value pairs"
    )
    
    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name = "Plan"
        verbose_name_plural = "Plans"
        indexes = [
            models.Index(fields=['status', 'plan_type']),
            models.Index(fields=['is_popular', 'sort_order']),
        ]
    
    def __str__(self):
        return f"{self.name} (${self.get_price_for_cycle('monthly')}/month)"
    
    def get_price_for_cycle(self, cycle):
        """Get price for specific billing cycle"""
        price_map = {
            'monthly': self.price_monthly,
            'quarterly': self.price_quarterly,
            'annually': self.price_annually,
            'biennial': self.price_biennial,
        }
        return price_map.get(cycle, self.price_monthly) or Decimal('0.00')
    
    def get_display_price(self, cycle='monthly'):
        """Get formatted price for display"""
        price = self.get_price_for_cycle(cycle)
        if price == Decimal('0.00'):
            return "Free"
        return f"${price}"
    
    def get_annual_savings_percentage(self):
        """Calculate annual savings percentage compared to monthly"""
        monthly_price = self.price_monthly
        annual_price = self.price_annually
        
        if not monthly_price or not annual_price:
            return 0
        
        monthly_total = monthly_price * 12
        if monthly_total <= annual_price:
            return 0
        
        savings = ((monthly_total - annual_price) / monthly_total) * 100
        return round(savings, 1)
    
    def has_trial(self):
        """Check if plan has trial period"""
        return self.trial_days > 0
    
    def is_free(self):
        """Check if plan is free"""
        return self.price_monthly == Decimal('0.00')
    
    def can_add_more_users(self, current_users):
        """Check if more users can be added"""
        if self.max_users is None:
            return True
        return current_users < self.max_users
    
    def get_feature_value(self, feature_key, default=None):
        """Get feature value from features JSON"""
        return self.features.get(feature_key, default)
    
    def has_feature(self, feature_key):
        """Check if plan has specific feature"""
        return feature_key in self.features and self.features[feature_key] is True
    
    def save(self, *args, **kwargs):
        # Auto-generate slug if not provided
        if not self.slug:
            self.slug = self.name.lower().replace(' ', '-').replace('_', '-')
        
        # Auto-calculate quarterly price if not set (3x monthly)
        if not self.price_quarterly and self.price_monthly:
            self.price_quarterly = self.price_monthly * 3
        
        # Auto-calculate annual price if not set (10x monthly for 20% discount)
        if not self.price_annually and self.price_monthly:
            self.price_annually = self.price_monthly * 10  # 20% discount on annual
        
        # Auto-calculate biennial price if not set (18x monthly for 25% discount)
        if not self.price_biennial and self.price_monthly:
            self.price_biennial = self.price_monthly * 18  # 25% discount on biennial
        
        super().save(*args, **kwargs)


class PlanFeature(models.Model):
    """
    Individual features that can be associated with plans
    """
    FEATURE_TYPES = [
        ('boolean', 'Boolean'),
        ('number', 'Number'),
        ('text', 'Text'),
        ('list', 'List'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    feature_type = models.CharField(max_length=20, choices=FEATURE_TYPES, default='boolean')
    default_value = models.JSONField(default=None, blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Icon class name")
    category = models.CharField(max_length=50, default='general')
    is_premium = models.BooleanField(default=False, help_text="Mark as premium feature")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'display_name']
        verbose_name = "Plan Feature"
        verbose_name_plural = "Plan Features"
    
    def __str__(self):
        return f"{self.display_name} ({self.feature_type})"


class PlanFeatureMapping(models.Model):
    """
    Many-to-many relationship between plans and features with values
    """
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='feature_mappings')
    feature = models.ForeignKey(PlanFeature, on_delete=models.CASCADE)
    value = models.JSONField(default=None, blank=True, help_text="Feature value for this plan")
    is_enabled = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['plan', 'feature']
        verbose_name = "Plan Feature Mapping"
        verbose_name_plural = "Plan Feature Mappings"
    
    def __str__(self):
        return f"{self.plan.name} - {self.feature.display_name}"


class Subscription(models.Model):
    """
    User subscription model for tracking plan subscriptions
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('trialing', 'Trial'),
        ('past_due', 'Past Due'),
        ('canceled', 'Canceled'),
        ('unpaid', 'Unpaid'),
        ('expired', 'Expired'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unpaid')
    
    # Billing cycle dates
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    trial_start = models.DateTimeField(null=True, blank=True)
    trial_end = models.DateTimeField(null=True, blank=True)
    
    # Payment information
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    currency = models.CharField(max_length=3, default='USD')
    
    # Metadata
    stripe_subscription_id = models.CharField(max_length=100, blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"
    
    def __str__(self):
        return f"{self.user.username} - {self.plan.name if self.plan else 'No Plan'} ({self.status})"
    
    def is_active(self):
        """Check if subscription is active"""
        return self.status in ['active', 'trialing']
    
    def is_paid(self):
        """Check if user has paid subscription"""
        return self.is_active() and self.plan and not self.plan.is_free()
    
    def needs_payment(self):
        """Check if user needs to make a payment"""
        if not self.plan or self.plan.is_free():
            return False
        return not self.is_active()
    
    def is_trial_active(self):
        """Check if trial is still active"""
        if self.status != 'trialing' or not self.trial_end:
            return False
        return timezone.now() < self.trial_end
    
    def get_trial_days_remaining(self):
        """Get remaining trial days"""
        if not self.is_trial_active():
            return 0
        delta = self.trial_end - timezone.now()
        return max(0, delta.days)


class Payment(models.Model):
    """
    Payment record model for tracking transactions
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('partially_refunded', 'Partially Refunded'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Payment gateway details
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True, null=True)
    payment_method = models.CharField(max_length=50, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
    
    def __str__(self):
        return f"{self.user.username} - ${self.amount} ({self.status})"
