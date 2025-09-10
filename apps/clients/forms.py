from django import forms
from apps.core.mixins import TailwindFormMixin
from .models import ClientProfile
from apps.progress.models import ClientProgress
from apps.trainers.models import TrainerProfile


class ClientProfileUpdateForm(TailwindFormMixin, forms.ModelForm):
    trainer = forms.ModelChoiceField(
        queryset=TrainerProfile.objects.filter(is_verified=True),
        required=True,
        label="Select Your Trainer",
        empty_label="-- Choose a Trainer --"
    )

    WEEKDAYS = [
    ('Mon', 'Monday'), ('Tue', 'Tuesday'), ('Wed', 'Wednesday'),
    ('Thu', 'Thursday'), ('Fri', 'Friday'), ('Sat', 'Saturday'), ('Sun', 'Sunday')
]
    preferred_workout_days = forms.MultipleChoiceField(
        choices=WEEKDAYS,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'flex flex-wrap gap-2'}),
        required=False
    )

    class Meta:
        model = ClientProfile
        fields = [
            'trainer', 'fitness_goal', 'fitness_level', 'height', 'current_weight',
            'target_weight', 'dietary_restrictions', 'medical_conditions',
            'allergies', 'preferred_workout_days', 'workout_duration_preference'
        ]
        widgets = {
            'medical_conditions': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'E.g., Asthma, knee injury, lactose intolerance',
                'class': 'w-full px-4 py-2 border border-primary-300 rounded-xl focus:ring-2 focus:ring-primary-400 focus:outline-none transition shadow-sm'
            }),
            'allergies': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'E.g., Peanut, Gluten, Lactose',
                'class': 'w-full px-4 py-2 border border-primary-300 rounded-xl focus:ring-2 focus:ring-primary-400 focus:outline-none transition shadow-sm'
            }),
            'workout_duration_preference': forms.NumberInput(attrs={
                'min': 10,
                'max': 180,
                'step': 5,
                'placeholder': 'Duration in minutes',
                'class': 'w-full px-4 py-2 border border-primary-300 rounded-xl focus:ring-2 focus:ring-primary-400 focus:outline-none transition shadow-sm'
            }),
     

        }
        
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.preferred_workout_days:
            raw = self.instance.preferred_workout_days
            cleaned = [d.strip() for d in raw.split(',') if d.strip()]
            print("Parsed days:", cleaned)

            # Set initial at both field and form level
            self.fields['preferred_workout_days'].initial = cleaned
            self.initial['preferred_workout_days'] = cleaned


class ClientEditProfileUpdateForm(TailwindFormMixin, forms.ModelForm):


    WEEKDAYS = [
    ('Mon', 'Monday'), ('Tue', 'Tuesday'), ('Wed', 'Wednesday'),
    ('Thu', 'Thursday'), ('Fri', 'Friday'), ('Sat', 'Saturday'), ('Sun', 'Sunday')
]

    preferred_workout_days = forms.MultipleChoiceField(
        choices=WEEKDAYS,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'flex flex-wrap gap-2'}),
        required=False
    )

    class Meta:
        model = ClientProfile
        fields = [
            'fitness_goal', 'fitness_level', 'height', 'current_weight',
            'target_weight', 'dietary_restrictions', 'medical_conditions',
            'allergies', 'preferred_workout_days', 'workout_duration_preference'
        ]
        exclude = ['trainer']  # exclude trainer from the form

        widgets = {
            'medical_conditions': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'E.g., Asthma, knee injury, lactose intolerance',
                'class': 'w-full px-4 py-2 border border-primary-300 rounded-xl focus:ring-2 focus:ring-primary-400 focus:outline-none transition shadow-sm'
            }),
            'allergies': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'E.g., Peanut, Gluten, Lactose',
                'class': 'w-full px-4 py-2 border border-primary-300 rounded-xl focus:ring-2 focus:ring-primary-400 focus:outline-none transition shadow-sm'
            }),
            'workout_duration_preference': forms.NumberInput(attrs={
                'min': 10,
                'max': 180,
                'step': 5,
                'placeholder': 'Duration in minutes',
                'class': 'w-full px-4 py-2 border border-primary-300 rounded-xl focus:ring-2 focus:ring-primary-400 focus:outline-none transition shadow-sm'
            }),
        }
        
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.preferred_workout_days:
            raw = self.instance.preferred_workout_days
            cleaned = [d.strip() for d in raw.split(',') if d.strip()]
            print("Parsed days:", cleaned)

            # Set initial at both field and form level
            self.fields['preferred_workout_days'].initial = cleaned
            self.initial['preferred_workout_days'] = cleaned
            
class ProgressLogForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = ClientProgress
        fields = [
            'date', 'current_weight', 'workout_completed', 'meal_plan_followed',
            'energy_level', 'sleep_hours', 'notes'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }



class ClientSetupProfileForm(TailwindFormMixin, forms.ModelForm):
    trainer = forms.ModelChoiceField(
        queryset=TrainerProfile.objects.filter(is_verified=True),
        empty_label="Select a trainer",
        widget=forms.RadioSelect
    )

    WEEKDAYS = [
        ('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'), ('Sunday', 'Sunday')
    ]
    preferred_workout_days = forms.MultipleChoiceField(
        choices=WEEKDAYS,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'flex flex-wrap gap-2'}),
        required=False
    )

    class Meta:
        model = ClientProfile
        fields = [
            'trainer', 'fitness_goal', 'fitness_level', 'height', 'current_weight',
            'target_weight', 'dietary_restrictions', 'medical_conditions',
            'allergies', 'preferred_workout_days', 'workout_duration_preference'
        ]
        widgets = {
            'medical_conditions': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'E.g., Asthma, knee injury, lactose intolerance',
                'class': 'w-full px-4 py-2 border border-primary-300 rounded-xl focus:ring-2 focus:ring-primary-400 focus:outline-none transition shadow-sm'
            }),
            'allergies': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'E.g., Peanut, Gluten, Lactose',
                'class': 'w-full px-4 py-2 border border-primary-300 rounded-xl focus:ring-2 focus:ring-primary-400 focus:outline-none transition shadow-sm'
            }),
            'workout_duration_preference': forms.NumberInput(attrs={
                'min': 10,
                'max': 180,
                'step': 5,
                'placeholder': 'Duration in minutes',
                'class': 'w-full px-4 py-2 border border-primary-300 rounded-xl focus:ring-2 focus:ring-primary-400 focus:outline-none transition shadow-sm'
            }),
        }
