from django import forms
from .models import ProgressGoal, ClientProgress
from apps.core.mixins import TailwindFormMixin
from django.utils import timezone
class ProgressGoalForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = ProgressGoal
        fields = [
            'client', 'title', 'description', 'goal_type', 'target_value',
            'current_value', 'unit', 'target_date'
        ]
        widgets = {
            'target_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        trainer = kwargs.pop('trainer', None)
        super().__init__(*args, **kwargs)

        if trainer:
            self.fields['client'].queryset = trainer.clients.filter(is_active=True)

class ClientProgressForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = ClientProgress
        fields = '__all__'
        exclude = ['client']
        widgets = {
            'sleep_hours': forms.NumberInput(attrs={'step': '0.5', 'min': '0'}),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-2 border rounded-xl'
            }),
        }
        
    def __init__(self, *args, **kwargs):
        self.client = kwargs.pop('client', None)  
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['date'].initial = timezone.now().date()
        if self.client:
            last_progress = ClientProgress.objects.filter(client=self.client).order_by('-date').first()
            if last_progress and not self.instance.pk:
                print(f'current weight: {last_progress.current_weight}')
                self.fields['current_weight'].initial = last_progress.current_weight

        # Apply Tailwind styling manually or via helper
     
    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')

        if self.client and date:
            exists = ClientProgress.objects.filter(client=self.client, date=date).exists()
            if exists:
                raise forms.ValidationError(f"A progress entry for {self.client} on {date} already exists.")
        return cleaned_data