from datetime import datetime, timedelta
from django import forms
from .models import Payment
from apps.clients.models import ClientProfile
from apps.core.mixins import TailwindFormMixin  # Assuming mixin lives here

class PaymentForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Payment
        fields = [
            'client', 'payment_type', 'amount', 'status', 'paid_date',  'due_date', 'description'
        ]
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'paid_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'amount': forms.NumberInput(attrs={'placeholder': 'Write the amount in ETB.'}),
        }

    def __init__(self, *args, **kwargs):
     trainer = kwargs.pop('trainer', None)
     super().__init__(*args, **kwargs)
 
     if trainer:
        self.fields['client'].queryset = trainer.clients.filter(is_active=True)

     # Pre-fill defaults
     self.fields['status'].initial = 'pending'  # example
     self.fields['payment_type'].initial = 'session'
     self.fields['paid_date'].initial = datetime.now()
     self.fields['due_date'].initial = datetime.now().date() + timedelta(days=30)
