# ai_services/forms.py

from django import forms

class WorkoutForm(forms.Form):
    name = forms.CharField()
    goal = forms.CharField()
    level = forms.CharField()
    equipment = forms.CharField()
    duration = forms.IntegerField()
    days = forms.MultipleChoiceField(choices=[('Mon', 'Monday'), ('Tue', 'Tuesday')])
    exercises = forms.MultipleChoiceField(choices=[('Pushups', 'Pushups'), ('Squats', 'Squats')])
