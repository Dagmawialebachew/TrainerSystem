from django.db import models
from django.urls import reverse

class ClientProgress(models.Model):
    """Track client progress and adherence"""
    
    ENERGY_LEVEL_CHOICES = [
        (1, 'Very Low'),
        (2, 'Low'),
        (3, 'Moderate'),
        (4, 'High'),
        (5, 'Very High'),
    ]
    
    client = models.ForeignKey(
        'clients.ClientProfile',
        on_delete=models.CASCADE,
        related_name='progress_entries'
    )
    
    # Date and basic metrics
    date = models.DateField()
    current_weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Adherence tracking
    workout_completed = models.BooleanField(default=False)
    meal_plan_followed = models.BooleanField(default=False)
    
    # Wellness metrics
    energy_level = models.PositiveIntegerField(choices=ENERGY_LEVEL_CHOICES, null=True, blank=True)
    sleep_hours = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    stress_level = models.PositiveIntegerField(choices=ENERGY_LEVEL_CHOICES, null=True, blank=True)
    
    # Body measurements (optional)
    chest_measurement = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    waist_measurement = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    hip_measurement = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    arm_measurement = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    thigh_measurement = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Notes and feedback
    notes = models.TextField(blank=True, help_text="How did you feel today?")
    trainer_feedback = models.TextField(blank=True, help_text="Trainer's feedback on this entry")
    
    # Photos (optional progress photos)
    progress_photo = models.ImageField(upload_to='progress_photos/', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
        unique_together = ['client', 'date']
    
    def __str__(self):
        return f"{self.client.user.get_full_name()} - {self.date}"
    
    @property
    def adherence_score(self):
        """Calculate daily adherence score (0-100)"""
        score = 0
        if self.workout_completed:
            score += 50
        if self.meal_plan_followed:
            score += 50
        return score

class ProgressGoal(models.Model):
    """Specific goals set by trainers for clients"""
    
    GOAL_TYPE_CHOICES = [
        ('weight', 'Weight Goal'),
        ('measurement', 'Body Measurement'),
        ('performance', 'Performance Goal'),
        ('habit', 'Habit Formation'),
        ('health', 'Health Metric'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('achieved', 'Achieved'),
        ('paused', 'Paused'),
        ('cancelled', 'Cancelled'),
    ]
    
    client = models.ForeignKey(
        'clients.ClientProfile',
        on_delete=models.CASCADE,
        related_name='goals'
    )
    trainer = models.ForeignKey(
        'trainers.TrainerProfile',
        on_delete=models.CASCADE,
        related_name='client_goals'
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPE_CHOICES)
    
    # Goal specifics
    target_value = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    current_value = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    unit = models.CharField(max_length=20, blank=True, help_text="kg, cm, reps, etc.")
    
    # Timeline
    target_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.client.user.get_full_name()}"
    
    @property
    def progress_percentage(self):
        """Calculate progress towards goal"""
        if self.target_value and self.current_value is not None:
            if self.target_value == 0:
                return 100 if self.current_value == 0 else 0
            return min(100, max(0, (self.current_value / self.target_value) * 100))
        return 0