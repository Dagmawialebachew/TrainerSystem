from django import forms
from django.contrib.auth import get_user_model
from .models import TrainerProfile
from apps.clients.models import ClientProfile
from apps.core.mixins import TailwindFormMixin  # adjust path if needed

User = get_user_model()


class TrainerProfileForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = TrainerProfile
        fields = [
            'business_name', 'bio', 'specializations', 'experience_years',
            'certifications', 'logo', 'brand_color', 'address', 'city',
            'website', 'instagram', 'hourly_rate', 'is_accepting_clients'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'help_text': "Write a brief professional bio (max 500 characters). Highlight your expertise, achievements, and what makes you unique."}),
            'certifications': forms.Textarea(attrs={'rows': 3}),
            'address': forms.Textarea(attrs={'rows': 2}),
            'brand_color': forms.TextInput(attrs={'type': 'color'}),
                        'logo': forms.ClearableFileInput(attrs={'class': 'text-sm'}),

        }
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # hide default clear text
            self.fields['logo'].widget.template_name = 'widgets/custom_clearable_file_input.html'


class ClientInviteForm(TailwindFormMixin, forms.ModelForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = ClientProfile
        fields = ['email', 'first_name', 'last_name', 'fitness_goal', 'fitness_level']

    def save(self, commit=True):
        # Create user account for client
        user = User.objects.create_user(
            username=self.cleaned_data['email'],
            email=self.cleaned_data['email'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            role='client'
        )

        # Create client profile
        client_profile = super().save(commit=False)
        client_profile.user = user

        if commit:
            client_profile.save()

        return client_profile

class ClientProfileUpdateForm(TailwindFormMixin, forms.ModelForm):


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

