from django.db import models
from django.urls import reverse

class MealPlan(models.Model):
    """Meal plans created by trainers for clients"""
    
    MEAL_TYPE_CHOICES = [
        ('weight_loss', 'Weight Loss'),
        ('muscle_gain', 'Muscle Gain'),
        ('maintenance', 'Maintenance'),
        ('performance', 'Performance'),
        ('therapeutic', 'Therapeutic'),
    ]
    
    trainer = models.ForeignKey(
        'trainers.TrainerProfile',
        on_delete=models.CASCADE,
        related_name='meal_plans'
    )
    client = models.ForeignKey(
        'clients.ClientProfile',
        on_delete=models.CASCADE,
        related_name='meal_plans'
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES, default='maintenance')
    
    # Nutritional targets
    daily_calories = models.PositiveIntegerField(null=True, blank=True)
    protein_grams = models.PositiveIntegerField(null=True, blank=True)
    carbs_grams = models.PositiveIntegerField(null=True, blank=True)
    fat_grams = models.PositiveIntegerField(null=True, blank=True)
    
    # Meal structure (JSON field for flexibility)
    meal_structure = models.JSONField(default=dict, help_text="Daily meal structure")
    
    # Ethiopian-specific considerations
    includes_traditional_foods = models.BooleanField(default=True)
    fasting_considerations = models.TextField(blank=True, help_text="Orthodox fasting considerations")
    
    # Status
    is_active = models.BooleanField(default=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    
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
        return reverse('nutrition:detail', kwargs={'pk': self.pk})

    
    
class TrainerFood(models.Model):
    """Foods added by specific trainers, enriched with cultural + dietary context"""

    trainer = models.ForeignKey(
        'trainers.TrainerProfile',
        on_delete=models.CASCADE,
        related_name='foods'
    )

    # Basic info
    name = models.CharField(max_length=200)
    
    FOOD_CATEGORY_CHOICES = [
        ('grains', 'Grains & Cereals'),
        ('legumes', 'Legumes'),
        ('vegetables', 'Vegetables'),
        ('fruits', 'Fruits'),
        ('meat', 'Meat & Poultry'),
        ('dairy', 'Dairy'),
        ('spices', 'Spices & Herbs'),
        ('beverages', 'Beverages'),
        ('traditional_dishes', 'Traditional Dishes'),
        ('other', 'Other'),
    ]
    category = models.CharField(max_length=30, choices=FOOD_CATEGORY_CHOICES, blank=True)

    # Nutrition (per 100g)
    calories_per_100g = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    protein_per_100g = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    carbs_per_100g = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    fat_per_100g = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    fiber_per_100g = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    # Contextual info
    description = models.TextField(blank=True)
    seasonal_availability = models.CharField(max_length=200, blank=True)
    cultural_significance = models.TextField(blank=True)
    preparation_notes = models.TextField(blank=True)

    # Dietary compatibility
    is_vegetarian = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)
    is_gluten_free = models.BooleanField(default=False)
    is_fasting_friendly = models.BooleanField(default=False, help_text="Orthodox fasting compatible")

    # Meta
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name}" 


class EthiopianFood(models.Model):
    """Database of Ethiopian foods for meal planning"""
    
    FOOD_CATEGORY_CHOICES = [
        ('grains', 'Grains & Cereals'),
        ('legumes', 'Legumes'),
        ('vegetables', 'Vegetables'),
        ('fruits', 'Fruits'),
        ('meat', 'Meat & Poultry'),
        ('dairy', 'Dairy'),
        ('spices', 'Spices & Herbs'),
        ('beverages', 'Beverages'),
        ('traditional_dishes', 'Traditional Dishes'),
    ]
    
    name = models.CharField(max_length=200)
    name_amharic = models.CharField(max_length=200, blank=True)
    category = models.CharField(max_length=30, choices=FOOD_CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    
    # Nutritional information (per 100g)
    calories_per_100g = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    protein_per_100g = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    carbs_per_100g = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    fat_per_100g = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    fiber_per_100g = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Availability & Cultural info
    seasonal_availability = models.CharField(max_length=200, blank=True)
    cultural_significance = models.TextField(blank=True)
    preparation_notes = models.TextField(blank=True)
    
    # Dietary compatibility
    is_vegetarian = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)
    is_gluten_free = models.BooleanField(default=False)
    is_fasting_friendly = models.BooleanField(default=False, help_text="Orthodox fasting compatible")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.name_amharic})" if self.name_amharic else self.name
    