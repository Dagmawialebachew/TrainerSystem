from django.db import models
from django.urls import reverse
from django.conf import settings
from django.utils import timezone

class ClientProfile(models.Model):
    """Extended profile for clients"""
    
    FITNESS_GOAL_CHOICES = [
        ('weight_loss', 'Weight Loss'),
        ('muscle_gain', 'Muscle Gain'),
        ('strength', 'Build Strength'),
        ('endurance', 'Improve Endurance'),
        ('flexibility', 'Increase Flexibility'),
        ('general_fitness', 'General Fitness'),
        ('rehabilitation', 'Rehabilitation'),
        ('sports_performance', 'Sports Performance'),
    ]
    
    FITNESS_LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    DIETARY_RESTRICTION_CHOICES = [
        ('none', 'No Restrictions'),
        ('vegetarian', 'Vegetarian'),
        ('vegan', 'Vegan'),
        ('halal', 'Halal'),
        ('gluten_free', 'Gluten Free'),
        ('dairy_free', 'Dairy Free'),
        ('diabetic', 'Diabetic Friendly'),
        ('low_sodium', 'Low Sodium'),
    ]
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='client_profile'
    )
    trainer = models.ForeignKey(
        'trainers.TrainerProfile',
        on_delete=models.CASCADE,
        related_name='clients'
    )

    
    # Fitness Information
    fitness_goal = models.CharField(max_length=30, choices=FITNESS_GOAL_CHOICES, default='general_fitness')
    fitness_level = models.CharField(max_length=20, choices=FITNESS_LEVEL_CHOICES, default='beginner')
    
    # Physical Information
    height = models.PositiveIntegerField(help_text="Height in cm", null=True, blank=True)
    current_weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Weight in kg")
    target_weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Target weight in kg")
    
    # Health & Dietary Information
    dietary_restrictions = models.CharField(max_length=30, choices=DIETARY_RESTRICTION_CHOICES, default='none')
    medical_conditions = models.TextField(blank=True, help_text="Any medical conditions or injuries")
    allergies = models.TextField(blank=True, help_text="Food allergies or intolerances")
    
    # Preferences
    preferred_workout_days = models.CharField(max_length=100, blank=True, help_text="e.g., Monday, Wednesday, Friday")
    workout_duration_preference = models.PositiveIntegerField(default=60, help_text="Preferred workout duration in minutes")
    
    # Status
    is_active = models.BooleanField(default=True)
    start_date = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True, help_text="Trainer notes about client")
    
    # Schedule
    weekly_sessions = models.PositiveIntegerField(default=3, help_text="Number of sessions per week")

    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.trainer.business_name or self.trainer.user.get_full_name()}"
    
    def get_absolute_url(self):
        return reverse('clients:profile')
    
    @property
    def current_bmi(self):
        if self.height and self.current_weight:
            height_m = self.height / 100
            return round(float(self.current_weight) / (height_m ** 2), 1)
        return None
    
    @property
    def weight_progress(self):
        if self.current_weight and self.target_weight:
            return float(self.current_weight) - float(self.target_weight)
        return None
    
    

