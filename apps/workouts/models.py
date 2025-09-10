from django.db import models
from django.urls import reverse
import json

class WorkoutPlan(models.Model):
    """Workout plans created by trainers for clients"""
    
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    trainer = models.ForeignKey(
        'trainers.TrainerProfile',
        on_delete=models.CASCADE,
        related_name='workout_plans'
    )
    client = models.ForeignKey(
        'clients.ClientProfile',
        on_delete=models.CASCADE,
        related_name='workout_plans'
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    # duration_weeks = models.PositiveIntegerField(default=4, help_text="Plan duration in weeks")
    
    # Workout structure (JSON field for flexibility)
    workout_structure = models.JSONField(default=dict, help_text="Weekly workout structure")
    
    # Status
    is_active = models.BooleanField(default=True)
    # start_date = models.DateField()
    # end_date = models.DateField(null=True, blank=True)
    
    # AI Enhancement
    ai_enhanced = models.BooleanField(default=False)
    ai_suggestions = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.client.user.get_full_name()}"
    
    def get_absolute_url(self):
        return reverse('workouts:detail', kwargs={'pk': self.pk})
    
    @property
    def formatted_structure(self):
        """Return formatted workout structure for display"""
        if not self.workout_structure:
            return {}
        return self.workout_structure

class Exercise(models.Model):
    """Exercise database for workout plans"""
    
    CATEGORY_CHOICES = [
        ('strength', 'Strength Training'),
        ('cardio', 'Cardiovascular'),
        ('flexibility', 'Flexibility'),
        ('balance', 'Balance'),
        ('functional', 'Functional'),
        ('sports', 'Sports Specific'),
    ]
    
    EQUIPMENT_CHOICES = [
        ('bodyweight', 'Bodyweight'),
        ('dumbbells', 'Dumbbells'),
        ('barbell', 'Barbell'),
        ('resistance_bands', 'Resistance Bands'),
        ('kettlebell', 'Kettlebell'),
        ('machine', 'Machine'),
        ('cardio_equipment', 'Cardio Equipment'),
        ('minimal', 'Minimal Equipment'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    equipment_needed = models.CharField(max_length=30, choices=EQUIPMENT_CHOICES, default='bodyweight')
    muscle_groups = models.CharField(max_length=200, help_text="Comma-separated muscle groups")
    
    # Instructions
    setup_instructions = models.TextField(help_text="How to set up the exercise")
    execution_steps = models.TextField(help_text="Step-by-step execution")
    safety_tips = models.TextField(blank=True)
    
    # Media
    demonstration_video_url = models.URLField(blank=True)
    image = models.ImageField(upload_to='exercises/', null=True, blank=True)
    
    # Difficulty & Modifications
    difficulty_level = models.CharField(max_length=20, choices=WorkoutPlan.DIFFICULTY_CHOICES, default='beginner')
    modifications = models.TextField(blank=True, help_text="Easier/harder variations")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name