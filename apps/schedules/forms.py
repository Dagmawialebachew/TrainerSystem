from django import forms
from .models import WorkoutSchedule, WorkoutSession, TimeBlock
from apps.core.mixins import TailwindFormMixin

class WorkoutScheduleForm(forms.ModelForm):
    class Meta:
        model = WorkoutSchedule
        fields = [
            'start_date', 'end_date',
            'weekly_sessions',
            'default_start_time', 'default_duration',
            'trainer_approve_required', 'notes'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date':   forms.DateInput(attrs={'type': 'date'}),
            'default_start_time': forms.TimeInput(attrs={'type': 'time'}),
            'default_duration':   forms.TextInput(attrs={'placeholder': 'HH:MM:SS'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

class WorkoutSessionForm(forms.ModelForm):
    class Meta:
        model = WorkoutSession
        fields = ['schedule', 'date', 'start_time', 'end_time', 'trainer_approved', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'input'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'input'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'input'}),
            'notes': forms.Textarea(attrs={'rows': 4, 'class': 'textarea'}),
        }

class TimeBlockForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = TimeBlock
        fields = ['session', 'start_time', 'end_time', 'notes']
