from django.db import models

# Create your models here.

class SiteSettings(models.Model):
    company_name = models.CharField(max_length=200, blank=True, default="")
    website_url = models.URLField(blank=True, default="")
    contact_email = models.EmailField(blank=True, default="")
    contact_phone = models.CharField(max_length=50, blank=True, default="")
    address = models.TextField(blank=True, default="")

    default_language = models.CharField(max_length=50, blank=True, default="English (United States)")
    time_zone = models.CharField(max_length=50, blank=True, default="UTC")
    date_format = models.CharField(max_length=20, blank=True, default="YYYY-MM-DD")
    time_format = models.CharField(max_length=20, blank=True, default="24-hour")
    first_day_of_week = models.IntegerField(blank=True, default=1)
    currency = models.CharField(max_length=50, blank=True, default="USD - US Dollar ($)")

    maintenance_mode = models.BooleanField(default=False)
    user_registration = models.BooleanField(default=True)
    email_verification = models.BooleanField(default=True)
    remember_me = models.BooleanField(default=True)
    show_tutorial = models.BooleanField(default=True)

    theme = models.CharField(max_length=10, blank=True, default="light")
    primary_color = models.CharField(max_length=7, blank=True, default="#0d6efd")
    fixed_header = models.BooleanField(default=True)
    fixed_sidebar = models.BooleanField(default=True)
    collapsed_sidebar = models.BooleanField(default=False)
    # Company branding
    company_logo = models.ImageField(upload_to='site/', blank=True, null=True)
    collapsed_logo = models.BooleanField(default=False)

    # Ticket settings
    default_ticket_status = models.CharField(max_length=50, blank=True, default="Open")
    default_ticket_priority = models.CharField(max_length=20, blank=True, default="Medium")
    auto_ticket_assignment = models.BooleanField(default=True)
    allow_ticket_reopen = models.BooleanField(default=True)
    first_response_hours = models.IntegerField(blank=True, default=24)
    resolution_time_hours = models.IntegerField(blank=True, default=72)
    sla_business_hours = models.CharField(max_length=100, blank=True, default="Business Hours (9 AM - 5 PM, Mon-Fri)")

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Site Settings ({self.pk})"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Faq(models.Model):
    """Simple FAQ entry model for user-visible help articles."""
    QUESTION_MAX = 512
    question = models.CharField(max_length=QUESTION_MAX)
    answer = models.TextField()
    category = models.CharField(max_length=120, blank=True, default='')
    order = models.IntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.question
