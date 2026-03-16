from django.contrib import admin
from .models import SiteSettings, Faq


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'website_url', 'contact_email', 'updated_at')


@admin.register(Faq)
class FaqAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'is_published', 'order')
    list_filter = ('category', 'is_published')
    search_fields = ('question', 'answer')
    ordering = ('order',)
from django.contrib import admin

# Register your models here.
