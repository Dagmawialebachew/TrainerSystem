from django.contrib import admin
from .models import Payment, Subscription

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('trainer', 'client', 'payment_type', 'amount', 'status', 'due_date', 'paid_date')
    list_filter = ('payment_type', 'status', 'currency', 'due_date')
    search_fields = ('trainer__business_name', 'client__user__first_name', 'client__user__last_name')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'due_date'
    
    fieldsets = (
        ('Parties', {
            'fields': ('trainer', 'client')
        }),
        ('Payment Details', {
            'fields': ('payment_type', 'amount', 'currency', 'description')
        }),
        ('Status & Tracking', {
            'fields': ('status', 'stripe_payment_intent_id', 'due_date', 'paid_date')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('trainer', 'package', 'status', 'monthly_amount', 'current_period_end')
    list_filter = ('package', 'status', 'currency')
    search_fields = ('trainer__business_name', 'trainer__user__first_name', 'trainer__user__last_name')
    readonly_fields = ('created_at', 'updated_at', 'is_active', 'is_trial')
    
    fieldsets = (
        ('Trainer', {
            'fields': ('trainer',)
        }),
        ('Subscription Details', {
            'fields': ('package', 'status', 'monthly_amount', 'currency')
        }),
        ('Stripe Integration', {
            'fields': ('stripe_subscription_id',)
        }),
        ('Billing Periods', {
            'fields': ('start_date', 'current_period_start', 'current_period_end', 'trial_end', 'cancelled_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )