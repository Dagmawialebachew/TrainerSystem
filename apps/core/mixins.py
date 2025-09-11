from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.conf import settings
from apps.trainers.models import TrainerProfile
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib import messages


class RoleRequiredMixin(UserPassesTestMixin):
    """Mixin to require specific user roles"""
    required_role = None
    
    def test_func(self):
        if not self.required_role:
            return True
        return self.request.user.role == self.required_role

class TrainerRequiredMixin(RoleRequiredMixin):
    """Mixin to require trainer role"""
    required_role = 'trainer'

class ClientRequiredMixin(RoleRequiredMixin):
    """Mixin to require client role"""
    required_role = 'client'

class AdminRequiredMixin(RoleRequiredMixin):
    """Mixin to require admin role"""
    required_role = 'admin'

class TrainerOwnedMixin:
    """Mixin to ensure objects belong to the current trainer"""
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if hasattr(self.request.user, 'trainer_profile'):
            return queryset.filter(trainer=self.request.user.trainer_profile)
        return queryset.none()

class PackageLimitMixin:
    """Mixin to enforce package limits"""
    limit_type = None  # 'max_clients', 'ai_features', 'custom_branding'
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_trainer:
            trainer_profile = get_object_or_404(TrainerProfile, user=request.user)
            package_limits = settings.PACKAGE_LIMITS.get(trainer_profile.package, {})
            
            if self.limit_type == 'max_clients':
                current_clients = trainer_profile.clients.count()
                max_clients = package_limits.get('max_clients', 0)
                if current_clients >= max_clients:
                    raise PermissionDenied("You have reached your client limit. Please upgrade your package.")
            
            elif self.limit_type == 'ai_features':
                if not package_limits.get('ai_features', False):
                    raise PermissionDenied("AI features are not available in your current package.")
            
            elif self.limit_type == 'custom_branding':
                if not package_limits.get('custom_branding', False):
                    raise PermissionDenied("Custom branding is not available in your current package.")
        
        return super().dispatch(request, *args, **kwargs)

class SubscriptionRequiredMixin:
    """
    Redirects trainers to pending payment if their subscription is inactive.
    Assumes user is authenticated and has a trainer_profile.
    """

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        # Ensure profile exists
        if not hasattr(user, "trainer_profile"):
            messages.error(request, "Please complete your profile first.")
            return redirect(reverse_lazy("trainers:setup_profile"))

        profile = user.trainer_profile

        # Check subscription status
        if not profile.is_paid:
            messages.info(request, "Your subscription is inactive. Please renew to continue.")
            return redirect(reverse_lazy("accounts:pending_payment"))

        return super().dispatch(request, *args, **kwargs)
    
class ClientOwnedMixin:
    """Mixin to ensure objects belong to the current client"""
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if hasattr(self.request.user, 'client_profile'):
            return queryset.filter(client=self.request.user.client_profile)
        return queryset.none()
    
    
# apps/core/forms.py
from django import forms

class TailwindFormMixin:
    """
    A reusable mixin that applies consistent TailwindCSS classes to all form fields,
    with special handling for textareas, file inputs, and color pickers.
    """
    default_input_class = (
        "w-full px-3 py-2 border border-gray-300 rounded-md "
        "focus:outline-none focus:ring-2 focus:ring-blue-500"
    )
    default_textarea_class = (
        "w-full px-3 py-2 border border-gray-300 rounded-md "
        "focus:outline-none focus:ring-2 focus:ring-blue-500"
    )
    
    default_select_class = (
    "w-[3rem] px-3 py-2 border border-gray-300 rounded-md bg-white text-gray-700 "
    "focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none")
    default_file_class = (
        "block w-full text-sm text-gray-700 border border-gray-300 rounded-md "
        "cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500"
    )
    default_color_class = "h-10 w-20 cursor-pointer rounded-md border border-gray-300"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            widget = field.widget

            if isinstance(widget, forms.Textarea):
                widget.attrs.setdefault("class", self.default_textarea_class)
                widget.attrs.setdefault("rows", 3)

            elif isinstance(widget, forms.FileInput):
                widget.attrs.setdefault("class", self.default_file_class)

            elif isinstance(widget, forms.TextInput) and widget.input_type == "color":
                widget.attrs.setdefault("class", self.default_color_class)
            elif isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault("class", self.default_select_class)

            else:
                widget.attrs.setdefault("class", self.default_input_class)





