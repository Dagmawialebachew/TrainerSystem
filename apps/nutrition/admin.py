from django.contrib import admin
from .models import MealPlan, EthiopianFood

@admin.register(MealPlan)
class MealPlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'trainer', 'client', 'meal_type', 'is_active', 'start_date')
    list_filter = ('meal_type', 'is_active', 'includes_traditional_foods', 'ai_enhanced')
    search_fields = ('title', 'client__user__first_name', 'client__user__last_name', 'trainer__business_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('trainer', 'client', 'title', 'description', 'meal_type')
        }),
        ('Nutritional Targets', {
            'fields': ('daily_calories', 'protein_grams', 'carbs_grams', 'fat_grams')
        }),
        ('Schedule', {
            'fields': ('start_date', 'end_date', 'is_active')
        }),
        ('Meal Structure', {
            'fields': ('meal_structure',)
        }),
        ('Ethiopian Considerations', {
            'fields': ('includes_traditional_foods', 'fasting_considerations')
        }),
        ('AI Enhancement', {
            'fields': ('ai_enhanced', 'ai_suggestions')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(EthiopianFood)
class EthiopianFoodAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_amharic', 'category', 'calories_per_100g', 'is_vegetarian', 'is_fasting_friendly')
    list_filter = ('category', 'is_vegetarian', 'is_vegan', 'is_gluten_free', 'is_fasting_friendly')
    search_fields = ('name', 'name_amharic', 'description')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'name_amharic', 'category', 'description')
        }),
        ('Nutritional Info', {
            'fields': ('calories_per_100g', 'protein_per_100g', 'carbs_per_100g', 'fat_per_100g', 'fiber_per_100g')
        }),
        ('Cultural & Availability', {
            'fields': ('seasonal_availability', 'cultural_significance', 'preparation_notes')
        }),
        ('Dietary Compatibility', {
            'fields': ('is_vegetarian', 'is_vegan', 'is_gluten_free', 'is_fasting_friendly')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at')
        }),
    )