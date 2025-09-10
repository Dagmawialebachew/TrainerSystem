from django.contrib import admin
from .models import ClientProfile

@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'trainer', 'fitness_goal', 'fitness_level', 'is_active', 'start_date')
    list_filter = ('fitness_goal', 'fitness_level', 'dietary_restrictions', 'is_active', 'start_date')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'updated_at', 'start_date')
    
    fieldsets = (
        ('User & Trainer', {
            'fields': ('user', 'trainer')
        }),
        ('Fitness Information', {
            'fields': ('fitness_goal', 'fitness_level', 'height', 'current_weight', 'target_weight')
        }),
        ('Health & Dietary', {
            'fields': ('dietary_restrictions', 'medical_conditions', 'allergies')
        }),
        ('Preferences', {
            'fields': ('preferred_workout_days', 'workout_duration_preference')
        }),
        ('Status & Notes', {
            'fields': ('is_active', 'notes')
        }),
        ('Timestamps', {
            'fields': ('start_date', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )