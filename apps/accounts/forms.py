from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

from apps.core.mixins import TailwindFormMixin

ROLE_CHOICES = [
    ('client', 'Client'),
    ('trainer', 'Trainer'),
]

from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm,
    PasswordResetForm,
    SetPasswordForm,
)
from .models import User


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Enter your username",
                "class": "w-full pl-10 pr-3 py-2 border border-neutral-300 rounded-lg "
                         "focus:ring-2 focus:ring-primary-500 focus:border-primary-500 "
                         "text-neutral-900 placeholder-neutral-400 text-sm"
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Enter your password",
                "class": "w-full pl-10 pr-3 py-2 border border-neutral-300 rounded-lg "
                         "focus:ring-2 focus:ring-primary-500 focus:border-primary-500 "
                         "text-neutral-900 placeholder-neutral-400 text-sm"
            }
        )
    )
    



class UserRegistrationForm(TailwindFormMixin, UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone_number = forms.CharField(max_length=15, required=False)
    role = forms.ChoiceField(choices=ROLE_CHOICES, label="I am a", initial="CLIENT")

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'role', 'password1', 'password2')

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 != password2:
            self.add_error('password2', "Passwords do not match")
            
            
class CustomFileInput(forms.ClearableFileInput):
    template_name = 'widgets/custom_clearable_file_input.html'
class ProfileUpdateForm(forms.ModelForm):
    
    class Meta:
        model = User
        fields = (
            "first_name", "last_name", "email",
            "phone_number", "date_of_birth", "profile_picture"
        )
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "w-full px-3 py-2 rounded-lg border border-gray-200"}),
            "last_name": forms.TextInput(attrs={"class": "w-full px-3 py-2 rounded-lg border border-gray-200"}),
            "email": forms.EmailInput(attrs={"class": "w-full px-3 py-2 rounded-lg border border-gray-200"}),
            "phone_number": forms.TextInput(attrs={"class": "w-full px-3 py-2 rounded-lg border border-gray-200"}),
            "date_of_birth": forms.DateInput(attrs={
                "type": "date",
                "class": "w-full px-3 py-2 rounded-lg border border-gray-200"
            }),
              'profile_picture': CustomFileInput(attrs={
                'id': 'id_profile_picture',
                'accept': 'image/jpeg,image/png,image/webp',
                'class': 'block w-full text-sm text-gray-700 appearance-none file:hidden',
            }),
        }

    def clean(self):
        cleaned = super().clean()
        # Require a profile picture only if the user doesn't already have one
        has_existing = bool(getattr(self.instance, "profile_picture", None) and self.instance.profile_picture)
        uploaded = self.files.get("profile_picture")
        if not has_existing and not uploaded:
            self.add_error("profile_picture", "Please upload a profile photo.")
        return