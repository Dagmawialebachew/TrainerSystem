from django import forms

from apps.trainers.models import TrainerProfile
from .models import MealPlan, TrainerFood
from apps.clients.models import ClientProfile
from apps.core.mixins import TailwindFormMixin

class MealPlanForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = MealPlan
        fields = [
            'client', 'title', 'description', 'meal_type', 'daily_calories',
            'protein_grams', 'carbs_grams', 'fat_grams', 'start_date',
            'includes_traditional_foods', 'fasting_considerations'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'placeholder': 'Select a start date for the meal plan'
            }),
            'title': forms.TextInput(attrs={
                'placeholder': 'e.g. High-Protein Week '
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Briefly describe the goal or theme of this meal plan'
            }),
            'meal_type': forms.Select(attrs={
                'placeholder': 'Choose the type of meals included'  # Note: placeholder won't show on <select>
            }),
            'daily_calories': forms.NumberInput(attrs={
                'placeholder': 'Target daily calorie intake (e.g. 2200)'
            }),
            'protein_grams': forms.NumberInput(attrs={
                'placeholder': 'Protein target in grams (e.g. 120)'
            }),
            'carbs_grams': forms.NumberInput(attrs={
                'placeholder': 'Carbohydrate target in grams (e.g. 250)'
            }),
            'fat_grams': forms.NumberInput(attrs={
                'placeholder': 'Fat target in grams (e.g. 70)'
            }),
            'fasting_considerations': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Mention any fasting rules or restrictions (e.g. no dairy on Wednesdays)'
            }),
        }

    def __init__(self, *args, trainer=None, **kwargs):
        super().__init__(*args, **kwargs)
        if trainer:
            self.fields['client'].queryset = trainer.clients.all()  # or whatever logic fits


       



class TrainerFoodForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = TrainerFood
        fields = [
            "name",
            "category",
            "calories_per_100g",
            "protein_per_100g",
            "carbs_per_100g",
            "fat_per_100g",
            "fiber_per_100g",
            "description",
            "seasonal_availability",
            "cultural_significance",
            "preparation_notes",
            "is_vegetarian",
            "is_vegan",
            "is_gluten_free",
            "is_fasting_friendly",
        ]

        widgets = {
            

            "category": forms.Select(
                attrs={
                    "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg "
                             "focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 "
                             "dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 "
                             "dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 "
                             "focus:ring-blue-500 focus:outline-none transition shadow-sm",
                             
                             
                }
            ),
            "cultural_significance": forms.Textarea(
                attrs={
                    "rows": 2,
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 "
                             "focus:ring-blue-500 focus:outline-none transition shadow-sm"
                }
            ),
            "preparation_notes": forms.Textarea(
                attrs={
                    "rows": 2,
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 "
                             "focus:ring-blue-500 focus:outline-none transition shadow-sm"
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        self.trainer = kwargs.pop('trainer', None)
        super().__init__(*args, **kwargs)
        if self.trainer:
          self.fields['category'].queryset = TrainerFood.objects.filter(trainer=self.trainer)
        # Only apply defaults when creating a new object (not editing)
        if not self.instance.pk:
            self.fields["category"].initial = "grains"
            self.fields["calories_per_100g"].initial = 100
            self.fields["protein_per_100g"].initial = 5
            self.fields["carbs_per_100g"].initial = 20
            self.fields["fat_per_100g"].initial = 1
            self.fields["fiber_per_100g"].initial = 2
            self.fields["is_fasting_friendly"].initial = False
            self.fields["is_vegetarian"].initial = True
            self.fields["is_vegan"].initial = False
            self.fields["is_gluten_free"].initial = False
            self.fields["description"].initial = "Basic nutritional placeholder. Update with specific details."
            self.fields["preparation_notes"].initial = "E.g., boil, fry, stew, serve with injera."