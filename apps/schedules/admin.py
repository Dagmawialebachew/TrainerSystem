from django.contrib import admin
from .models import WorkoutSchedule, WorkoutSession, TimeBlock

@admin.register(WorkoutSchedule)
class WorkoutScheduleAdmin(admin.ModelAdmin):
    list_display = ['client', 'workout_plan', 'weekly_sessions', 'trainer_approve_required', 'created_at']
    list_filter = ['trainer_approve_required', 'weekly_sessions', 'created_at']


@admin.register(WorkoutSession)
class WorkoutSessionAdmin(admin.ModelAdmin):
    list_display = ['schedule', 'date', 'start_time', 'end_time', 'trainer_approved']
    list_filter = ['trainer_approved', 'date']


@admin.register(TimeBlock)
class TimeBlockAdmin(admin.ModelAdmin):
    list_display = ['session', 'start_time', 'end_time']
    list_filter = ['start_time']
