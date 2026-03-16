from django.contrib import admin


# Register your models here.
from superadmin.models import Company, Plan, Notification, SuperAdminSettings, SubscriptionMetrics

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'plan', 'subscription_status']

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'billing_cycle', 'status']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'notification_type', 'priority', 'user', 'is_read', 'created_at']
    list_filter = ['notification_type', 'priority', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'user__username']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        # SuperAdmins can see all notifications, others only see their own
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user) | qs.filter(user__isnull=True)


@admin.register(SuperAdminSettings)
class SuperAdminSettingsAdmin(admin.ModelAdmin):
    list_display = ['user', 'profile_name', 'email_notifications', 'dark_mode', 'currency']
    list_filter = ['email_notifications', 'in_app_notifications', 'dark_mode', 'language', 'currency']
    search_fields = ['user__username', 'profile_name', 'profile_email']


@admin.register(SubscriptionMetrics)
class SubscriptionMetricsAdmin(admin.ModelAdmin):
    list_display = ['date', 'active_subscriptions', 'new_subscriptions', 'monthly_revenue', 'mrr']
    list_filter = ['date']
    ordering = ['-date']


