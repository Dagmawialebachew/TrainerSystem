from apps.trainers.models import TrainerProfile
from django.db import models
from django.urls import reverse

class Payment(models.Model):
    """Track payments from clients to trainers"""
    
    PAYMENT_TYPE_CHOICES = [
        ('session', 'Training Session'),
        ('monthly', 'Monthly Package'),
        ('plan', 'Custom Plan'),
        ('consultation', 'Consultation'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    trainer = models.ForeignKey(
        'trainers.TrainerProfile',
        on_delete=models.CASCADE,
        related_name='payments_received'
    )
    client = models.ForeignKey(
        'clients.ClientProfile',
        on_delete=models.CASCADE,
        related_name='payments_made'
    )
    
    # Payment details
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=3, default='ETB')
    
    # Status and tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    stripe_payment_intent_id = models.CharField(max_length=200, blank=True)
    
    # Dates
    due_date = models.DateField()
    paid_date = models.DateTimeField(null=True, blank=True)
    
    # Description and notes
    description = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.payment_type} - {self.client.user.get_full_name()} - {self.amount} {self.currency}"

class Subscription(models.Model):
    """Track trainer subscriptions to the SaaS platform"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('past_due', 'Past Due'),
        ('cancelled', 'Cancelled'),
        ('trialing', 'Trialing'),
    ]
    
    trainer = models.OneToOneField(
        'trainers.TrainerProfile',
        on_delete=models.CASCADE,
        related_name='subscription'
    )
    
    # Subscription details
    package = models.CharField(max_length=20, choices=TrainerProfile.PACKAGE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='trialing')
    
    # Billing
    monthly_amount = models.DecimalField(max_digits=6, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    stripe_subscription_id = models.CharField(max_length=200, blank=True)
    
    # Dates
    start_date = models.DateTimeField()
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
    trial_end = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.trainer.business_name or self.trainer.user.get_full_name()} - {self.package}"
    
    @property
    def is_active(self):
        return self.status == 'active'
    
    @property
    def is_trial(self):
        return self.status == 'trialing'