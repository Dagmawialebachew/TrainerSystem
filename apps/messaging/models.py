from django.db import models
from django.urls import reverse

class EngagementMessage(models.Model):
    """Motivational and engagement messages sent to clients"""
    
    MESSAGE_TYPE_CHOICES = [
        ('motivational', 'Motivational'),
        ('reminder', 'Reminder'),
        ('congratulations', 'Congratulations'),
        ('check_in', 'Check-in'),
        ('educational', 'Educational'),
        ('custom', 'Custom'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    trainer = models.ForeignKey(
        'trainers.TrainerProfile',
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    client = models.ForeignKey(
        'clients.ClientProfile',
        on_delete=models.CASCADE,
        related_name='received_messages'
    )
    
    # Message content
    subject = models.CharField(max_length=200)
    message = models.TextField()
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES, default='custom')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    
    # Scheduling
    scheduled_for = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    # Engagement tracking
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # AI generation
    ai_generated = models.BooleanField(default=False)
    ai_prompt_used = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.subject} - {self.client.user.get_full_name()}"
    
    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])

class MessageTemplate(models.Model):
    """Pre-defined message templates for trainers"""
    
    trainer = models.ForeignKey(
        'trainers.TrainerProfile',
        on_delete=models.CASCADE,
        related_name='message_templates'
    )
    
    name = models.CharField(max_length=100)
    subject_template = models.CharField(max_length=200)
    message_template = models.TextField()
    message_type = models.CharField(max_length=20, choices=EngagementMessage.MESSAGE_TYPE_CHOICES)
    
    # Template variables (JSON field for flexibility)
    available_variables = models.JSONField(
        default=list,
        help_text="Available template variables like {client_name}, {goal}, etc."
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.trainer.business_name or self.trainer.user.get_full_name()}"