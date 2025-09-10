from django.contrib import admin
from .models import TrainerProfile

@admin.register(TrainerProfile)
class TrainerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'business_name', 'package', 'client_count', 'is_accepting_clients', 'created_at')
    list_filter = ('package', 'specializations', 'is_accepting_clients', 'created_at')
    search_fields = ('user__username', 'user__email', 'business_name')
    readonly_fields = ('created_at', 'updated_at', 'package_start_date')
    
    fieldsets = (
        ('User Info', {
            'fields': ('user',)
        }),
        ('Business Info', {
            'fields': ('business_name', 'bio', 'specializations', 'experience_years', 'certifications')
        }),
        ('Package & Billing', {
            'fields': ('package', 'package_start_date')
        }),
        ('Branding', {
            'fields': ('logo', 'brand_color')
        }),
        ('Contact & Location', {
            'fields': ('address', 'city', 'website', 'instagram')
        }),
        ('Settings', {
            'fields': ('hourly_rate', 'is_accepting_clients', 'is_paid')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )