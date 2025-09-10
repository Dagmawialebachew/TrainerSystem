from django.contrib import admin
from .models import ClientProgress, ProgressGoal

@admin.register(ClientProgress)
class ClientProgressAdmin(admin.ModelAdmin):
    list_display = ('client', 'date', 'current_weight', 'workout_completed', 'meal_plan_followed', 'energy_level')
    list_filter = ('workout_completed', 'meal_plan_followed', 'energy_level', 'date')
    search_fields = ('client__user__first_name', 'client__user__last_name')
    readonly_fields = ('created_at', 'updated_at', 'adherence_score')
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('client', 'date', 'current_weight')
        }),
        ('Adherence', {
            'fields': ('workout_completed', 'meal_plan_followed')
        }),
        ('Wellness', {
            'fields': ('energy_level', 'sleep_hours', 'stress_level')
        }),
        ('Measurements', {
            'fields': ('chest_measurement', 'waist_measurement', 'hip_measurement', 'arm_measurement', 'thigh_measurement')
        }),
        ('Notes & Media', {
            'fields': ('notes', 'trainer_feedback', 'progress_photo')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ProgressGoal)
class ProgressGoalAdmin(admin.ModelAdmin):
    list_display = ('title', 'client', 'trainer', 'goal_type', 'status', 'target_date', 'progress_percentage')
    list_filter = ('goal_type', 'status', 'target_date')
    search_fields = ('title', 'client__user__first_name', 'client__user__last_name')
    readonly_fields = ('created_at', 'updated_at', 'progress_percentage')
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('client', 'trainer', 'title', 'description', 'goal_type')
        }),
        ('Goal Details', {
            'fields': ('target_value', 'current_value', 'unit', 'target_date', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )