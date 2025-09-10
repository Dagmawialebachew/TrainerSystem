from django.contrib import admin
from .models import WorkoutPlan, Exercise

@admin.register(WorkoutPlan)
class WorkoutPlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'trainer', 'client', 'difficulty', 'is_active')
    list_filter = ('difficulty', 'is_active', 'ai_enhanced', 'created_at')
    search_fields = ('title', 'client__user__first_name', 'client__user__last_name', 'trainer__business_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('trainer', 'client', 'title', 'description', 'difficulty')
        }),
       
        ('Workout Structure', {
            'fields': ('workout_structure',)
        }),
        ('AI Enhancement', {
            'fields': ('ai_enhanced', 'ai_suggestions')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'equipment_needed', 'difficulty_level', 'is_active')
    list_filter = ('category', 'equipment_needed', 'difficulty_level', 'is_active')
    search_fields = ('name', 'muscle_groups')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'description', 'category', 'equipment_needed', 'muscle_groups')
        }),
        ('Instructions', {
            'fields': ('setup_instructions', 'execution_steps', 'safety_tips')
        }),
        ('Media', {
            'fields': ('demonstration_video_url', 'image')
        }),
        ('Difficulty & Modifications', {
            'fields': ('difficulty_level', 'modifications')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at')
        }),
    )