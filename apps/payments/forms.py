from django import forms
from .models import Payment
from apps.clients.models import ClientProfile
from apps.core.mixins import TailwindFormMixin  # Assuming mixin lives here

class PaymentForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Payment
        fields = [
            'client', 'payment_type', 'amount', 'due_date', 'description'
        ]
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        trainer = kwargs.pop('trainer', None)
        super().__init__(*args, **kwargs)

        if trainer:
            self.fields['client'].queryset = trainer.clients.filter(is_active=True)
