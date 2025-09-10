from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import User
from .forms import UserRegistrationForm, ProfileUpdateForm, CustomLoginForm
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetView,
)
from django.shortcuts import redirect
from django.contrib.auth import login
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import User
from .forms import UserRegistrationForm

class RegisterView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:setup_profile')

    def form_valid(self, form):
        user = form.save(commit=False)
        # Assign role based on selection
        user.role = form.cleaned_data.get('role', 'CLIENT').lower()
        user.save()
        login(self.request, user)
        messages.success(self.request, 'Account created successfully!')
        # Redirect based on role
        if user.role == 'trainer':
            return redirect('trainers:setup_profile')
        return redirect('clients:setup_profile')
    
    def form_invalid(self, form):
        # Loop through each field and its errors
        for field, errors in form.errors.items():
            for error in errors:
                if field == '__all__':
                    # Non-field errors
                    messages.error(self.request, f"{error}")
                else:
                    messages.error(self.request, f"{form.fields[field].label}: {error}")
        return super().form_invalid(form)

class CustomLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = CustomLoginForm

    def get_form_kwargs(self):
        """Ensure form is unbound on GET so no errors show on page load."""
        kwargs = super().get_form_kwargs()
        if self.request.method != "POST":
            kwargs["data"] = None
            kwargs["files"] = None
        return kwargs

    def form_valid(self, form):
        """Handle login based on verification and onboarding status."""
        user = form.get_user()
        login(self.request, user)
        messages.success(self.request, f"Welcome back, {user.username} 🎉")
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        if self.request.method == "POST":
            for field, errors in form.errors.items():
                for error in errors:
                    if field == "__all__":
                        messages.error(self.request, error)
                    else:
                        messages.error(self.request, f"{field.capitalize()}: {error}")

        # 🚨 redirect instead of rendering again
        return redirect(reverse_lazy("accounts:login"))

    def get_success_url(self):
        """Role-based redirects."""
        user = self.request.user
        if user.is_admin:
            return reverse_lazy("admin:index")
        elif user.is_client:
            if hasattr(user, 'client_profile'):
                return reverse_lazy("clients:dashboard")
            else:
                messages.error(self.request, 'Please first finish setting up your profile.')
                return reverse_lazy('clients:setup_profile')
        elif user.is_trainer:
            if not user.is_active_subscription:
                messages.error(self.request, "Your account is not yet verified by the Super Admin.")
                return reverse_lazy("accounts:pending_approval")
            return reverse_lazy("trainers:dashboard")

        return reverse_lazy("home")
    
class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileUpdateForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)
    

from django.views.generic import TemplateView

class PendingApprovalView(TemplateView):
    template_name = "accounts/pending_approval.html"

class PendingPaymentView(TemplateView):
    template_name = "accounts/pending_payment.html"
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        profile = self.request.user.trainer_profile
        # status = profile.subscription_status  # e.g., "pending" | "expired" | "grace"

        ctx.update({
            # "reason": status,
            "plan_name": profile.package,
            # "amount_due": profile.amount_due,
            # "currency": profile.currency,
            # "period_label": profile.billing_period_label,  # e.g., "Monthly"
            # "invoice_id": getattr(profile, "invoice_id", None),
            # "expired_on": getattr(profile, "expired_on", None),
            # "grace_ends_on": getattr(profile, "grace_ends_on", None),
            # "renew_until": getattr(profile, "renew_until", None),
            "support_phone": "+251960306801",
            "support_email": "support@yourbrand.com",
        })
        return ctx

