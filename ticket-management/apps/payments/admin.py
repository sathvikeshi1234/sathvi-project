"""
Admin configuration for payments app
"""

from django.contrib import admin
from superadmin.models import Payment, Subscription




@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    
    list_display = [
        'transaction_id', 
        'get_subscription_display', 
        'company', 
        'amount', 
        'status', 
        'payment_method', 
        'payment_date',
        'created_at'
    ]
    list_filter = [
        'status', 
        'payment_method', 
        'payment_date', 
        'created_at'
    ]
    search_fields = [
        'transaction_id', 
        'subscription__company__name',
        'invoice_number'
    ]
    readonly_fields = [
        'transaction_id', 
        'created_at', 
        'updated_at'
    ]
    ordering = ['-created_at']
    
    def get_subscription_display(self, obj):
        if obj.subscription:
            return f"{obj.subscription.company.name} - {obj.subscription.plan.name}"
        return "No subscription"
    get_subscription_display.short_description = 'Subscription'
    
    fieldsets = (
        ('Payment Information', {
            'fields': (
                'subscription',
                'company',
                'amount',
                'payment_method',
                'payment_type',
                'status'
            )
        }),
        ('Transaction Details', {
            'fields': (
                'transaction_id',
                'invoice_number',
                'payment_date',
                'gateway_fee'
            )
        }),
        ('Refund Information', {
            'fields': (
                'refund_amount',
                'refund_reason',
                'refunded_at'
            ),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': (
                'notes',
                'created_by',
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        })
    )


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ['transaction_id', 'created_at']
    fields = [
        'transaction_id',
        'amount',
        'payment_method',
        'status',
        'payment_date',
        'created_at'
    ]


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        'company',
        'plan',
        'status',
        'start_date',
        'end_date',
        'next_billing_date',
        'total_amount',
        'auto_renew'
    ]
    list_filter = [
        'status',
        'billing_cycle',
        'auto_renew',
        'start_date',
        'end_date'
    ]
    search_fields = [
        'company__name',
        'plan__name'
    ]
    readonly_fields = ['created_at', 'updated_at']
    inlines = [PaymentInline]
    ordering = ['-created_at']
    
    fieldsets = (
        ('Subscription Information', {
            'fields': (
                'company',
                'plan',
                'status',
                'billing_cycle'
            )
        }),
        ('Dates', {
            'fields': (
                'start_date',
                'end_date',
                'next_billing_date',
                'cancelled_at'
            )
        }),
        ('Pricing', {
            'fields': (
                'base_price',
                'discount_amount',
                'tax_amount',
                'total_amount'
            )
        }),
        ('Settings', {
            'fields': (
                'auto_renew',
                'notes'
            )
        }),
        ('System Information', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        })
    )
