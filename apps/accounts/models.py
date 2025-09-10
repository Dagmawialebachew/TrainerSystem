from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """Custom User model with role-based access"""
    
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('trainer', 'Trainer'),
        ('client', 'Client'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')
    phone_number = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    is_active_subscription = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
  
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_trainer(self):
        return self.role == 'trainer'
    
    @property
    def is_client(self):
        return self.role == 'client'
    
    @property
    def is_admin(self):
        return self.role == 'admin'
