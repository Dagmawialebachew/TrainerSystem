from django.contrib import admin
from .models import EngagementMessage, MessageTemplate

@admin.register(EngagementMessage)
class EngagementMessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'trainer', 'client', 'message_type', 'priority', 'is_read', 'sent_at')
    list_filter = ('message_type', 'priority', 'is_read', 'ai_generated', 'sent_at')
    search_fields = ('subject', 'client__user__first_name', 'client__user__last_name', 'trainer__business_name')
    readonly_fields = ('created_at', 'updated_at', 'sent_at', 'read_at')
    date_hierarchy = 'sent_at'
    
    fieldsets = (
        ('Parties', {
            'fields': ('trainer', 'client')
        }),
        ('Message Content', {
            'fields': ('subject', 'message', 'message_type', 'priority')
        }),
        ('Scheduling', {
            'fields': ('scheduled_for', 'sent_at')
        }),
        ('Engagement', {
            'fields': ('is_read', 'read_at')
        }),
        ('AI Generation', {
            'fields': ('ai_generated', 'ai_prompt_used')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(MessageTemplate)
class MessageTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'trainer', 'message_type', 'is_active', 'created_at')
    list_filter = ('message_type', 'is_active', 'created_at')
    search_fields = ('name', 'trainer__business_name', 'subject_template')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('trainer', 'name', 'message_type', 'is_active')
        }),
        ('Template Content', {
            'fields': ('subject_template', 'message_template')
        }),
        ('Variables', {
            'fields': ('available_variables',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )