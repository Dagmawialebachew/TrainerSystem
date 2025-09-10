from django import forms
from .models import WorkoutPlan
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
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Brief description of the workout'}),
            'workout_structure': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        trainer = kwargs.pop('trainer', None)
        super().__init__(*args, **kwargs)
        if trainer:
            self.fields['client'].queryset = trainer.clients.filter(is_active=True)