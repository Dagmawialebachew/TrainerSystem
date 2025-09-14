from django import forms
from .models import Exercise, WorkoutPlan
from apps.clients.models import ClientProfile
from apps.trainers.models import TrainerProfile
from apps.core.mixins import TailwindFormMixin

class WorkoutPlanForm(TailwindFormMixin, forms.ModelForm):
    goal = forms.ChoiceField(
        choices=[
            ('muscle_gain', 'Muscle Gain'),
            ('fat_loss', 'Fat Loss'),
            ('endurance', 'Endurance'),
            ('strength', 'Strength'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
   
    include_warmup_cooldown = forms.BooleanField(
        required=False, initial=True,
        widget=forms.CheckboxInput()
    )

    class Meta:
        model = WorkoutPlan
        fields = [
            'client', 'title', 'description', 'difficulty', 'workout_structure'
        ]
        widgets = {
 'description': forms.Textarea(attrs={
                'placeholder': 'Describe the plan goals, special notes, or instructions for the client.',
                'rows': 1,
            }),
 'difficulty': forms.Select(attrs={
                'placeholder': 'Select difficulty level (Beginner/Intermediate/Advanced)'
            }),
 'workout_structure': forms.HiddenInput(),
             'title': forms.TextInput(attrs={
                'placeholder': 'Full Body Strength Plan, Upper Body Focus, etc.'
            }),
        }

    def __init__(self, *args, **kwargs):
        trainer = kwargs.pop('trainer', None)
        super().__init__(*args, **kwargs)
        if trainer:
            self.fields['client'].queryset = trainer.clients.filter(is_active=True)
            
            
            


class ExerciseForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Exercise
        fields = [
            'name', 'category', 'equipment_needed', 'muscle_groups',
            'setup_instructions', 'execution_steps', 'safety_tips',
            'demonstration_video_url', 'image', 'difficulty_level', 'modifications', 'is_active'
        ]
        exclude = ['description']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Example: Push-Up, Dumbbell Curl'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Example: Bodyweight exercise for chest and arms'}),
            'category': forms.Select(),
            'equipment_needed': forms.Select(),
            'muscle_groups': forms.TextInput(attrs={'placeholder': 'Example: Chest, Triceps'}),
            'setup_instructions': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Optional: Get into plank position'}),
            'execution_steps': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Example: Lower body until chest almost touches floor, then push up'}),
            'safety_tips': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Optional: Keep back straight, do not lock elbows'}),
            'demonstration_video_url': forms.URLInput(attrs={'placeholder': 'Optional: https://youtube.com/...'}),
            'modifications': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Optional: Do on knees to make easier, add weight to make harder'}),
            'difficulty_level': forms.Select(),
            'is_active': forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        self.trainer = kwargs.pop('trainer', None)
        super().__init__(*args, **kwargs)
