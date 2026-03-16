from django.db import models

# Create your models here.
from django.contrib.auth.models import User


class Role(models.Model):
    ROLE_CHOICES = [
        ('SuperAdmin', 'SuperAdmin'),
        ('Admin', 'Admin'),
        ('Agent', 'Agent'),
        ('User', 'User'),
    ]
    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)

    class Meta:
        app_label = 'users'

    def __str__(self):
        return self.name
    

    # USER PROFILE MODEL
# -------------------------------------------------------
class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('', 'Not specified'),
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    employee_id = models.CharField(max_length=50, blank=True, null=True)
    join_date = models.DateField(blank=True, null=True)
    skills = models.TextField(blank=True, null=True, help_text="Comma-separated list of skills")
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    # Per-user UI/settings preferences for user dashboard
    dark_mode = models.BooleanField(default=False)
    theme = models.CharField(max_length=20, default='teal')
    email_notifications = models.BooleanField(default=True)
    desktop_notifications = models.BooleanField(default=False)
    show_activity_status = models.BooleanField(default=True)
    allow_dm_from_non_contacts = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)
    
    # Security and notification settings
    login_alerts = models.BooleanField(default=True)
    security_alerts = models.BooleanField(default=True)
    session_timeout = models.IntegerField(default=30)  # minutes
    
    # Activity tracking
    last_active = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"
