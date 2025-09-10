from django import forms
from .models import EngagementMessage, MessageTemplate
from apps.clients.models import ClientProfile

class EngagementMessageForm(forms.ModelForm):
    class Meta:
        model = EngagementMessage
        fields = [
            'client', 'subject', 'message', 'message_type', 'priority', 'scheduled_for'
        ]
        widgets = {
            'scheduled_for': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'message': forms.Textarea(attrs={'rows': 6}),
        }
    
    def __init__(self, *args, **kwargs):
        trainer = kwargs.pop('trainer', None)
        super().__init__(*args, **kwargs)
        
        if trainer:
            self.fields['client'].queryset = trainer.clients.filter(is_active=True)
        
        for field_name, field in self.fields.items():
            if field_name != 'message':
                field.widget.attrs['class'] = 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            else:
                field.widget.attrs['class'] = 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'

class MessageTemplateForm(forms.ModelForm):
    class Meta:
        model = MessageTemplate
        fields = [
            'name', 'subject_template', 'message_template', 'message_type', 'available_variables'
        ]
        widgets = {
            'message_template': forms.Textarea(attrs={'rows': 6}),
            'available_variables': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Enter available variables as JSON array, e.g., ["client_name", "goal", "progress"]'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name not in ['message_template', 'available_variables']:
                field.widget.attrs['class'] = 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            else:
                field.widget.attrs['class'] = 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'