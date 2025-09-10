from datetime import datetime
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, CreateView, UpdateView, ListView, DetailView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from apps.core.mixins import TrainerRequiredMixin, PackageLimitMixin, SubscriptionRequiredMixin
from apps.clients.models import ClientProfile
from apps.payments.models import Payment
from apps.schedules.models import WorkoutSession
from apps.workouts.models import WorkoutPlan
from apps.nutrition.models import MealPlan
from apps.progress.models import ClientProgress
from .models import TrainerProfile
from .forms import TrainerProfileForm, ClientInviteForm, ClientProfileUpdateForm
from django.db.models import Avg, Count, Q


class TrainerDashboardView(LoginRequiredMixin,TrainerRequiredMixin,SubscriptionRequiredMixin, TemplateView):
    template_name = 'trainers/dashboard.html'
    
    def dispatch(self, request, *args, **kwargs):
        user = request.user

        # 1. Check if the user has a trainer_profile
        if not hasattr(user, "trainer_profile"):
            messages.error(request, 'Please complete your profile to access the dashboard.')
            return redirect(reverse_lazy("trainers:setup_profile"))

        # 2. Check if the subscription is inactive
        if not user.is_active_subscription:
            return redirect(reverse_lazy("accounts:pending_approval"))
        elif not user.trainer_profile.is_paid:
            return redirect(reverse_lazy("accounts:pending_payment"))

        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
      
            context = super().get_context_data(**kwargs)
            trainer_profile, created = TrainerProfile.objects.get_or_create(user=self.request.user)
            # Dashboard stats
            total_clients = trainer_profile.clients.count()
            active_clients = trainer_profile.clients.filter(is_active=True).count()
            workout_plans = WorkoutPlan.objects.filter(trainer=trainer_profile).count()
            meal_plans = MealPlan.objects.filter(trainer=trainer_profile).count()
            profile = self.request.user.trainer_profile
            sessions =  WorkoutSession.objects.filter(
    schedule__trainer=self.request.user.trainer_profile,
    date=timezone.localdate()
).order_by("updated_at")
            now = timezone.now()
            today = now.date()
            # Build the cards list in Python
            card = [
                {'icon': 'users', 'title': 'Total Clients', 'value': total_clients, 'color': 'bg-gradient-to-tr from-primary-100 to-primary-300'},
                {'icon': 'check-circle', 'title': 'Active Clients', 'value': active_clients, 'color': 'bg-gradient-to-tr from-green-100 to-green-300'},
                {'icon': 'lightning-bolt', 'title': 'Workout Plans', 'value': workout_plans, 'color': 'bg-gradient-to-tr from-blue-100 to-blue-300'},
                {'icon': 'clipboard-list', 'title': 'Meal Plans', 'value': meal_plans, 'color': 'bg-gradient-to-tr from-orange-100 to-orange-300'},
            ]
            
            for session in sessions:
                if session.start_time > now.time():
                    start_dt = datetime.combine(today, session.start_time)
                    start_dt = timezone.make_aware(start_dt)  # 👈 this adds timezone info
                    delta = start_dt - now
                    session.hours_until = int(delta.total_seconds() // 3600)
                else:
                    session.hours_until = None

            context["todays_sessions"] = sessions
            context["now"] = now.time()

            # Add other context as needed
            context.update({
                'trainer_profile': trainer_profile,
                'recent_clients': trainer_profile.clients.order_by('-created_at')[:3],
                'recent_progress': ClientProgress.objects.filter(
                    client__trainer=trainer_profile
                ).order_by('-date')[:3],
                "recent_payments": Payment.objects.filter(trainer=profile).order_by("-paid_date")[:3],
                'cards': card,
            })
                
            return context

class SetupProfileView(LoginRequiredMixin,TrainerRequiredMixin,CreateView):
    model = TrainerProfile
    form_class = TrainerProfileForm
    template_name = 'trainers/setup_profile.html'
    success_url = reverse_lazy('trainers:dashboard')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Profile setup completed successfully!')
        return super().form_valid(form)
    def form_invalid(self, form):
        # Highlight which section to open
        self.extra_context = self.get_context_data(form=form)
        
        # Add error messages for the user
        for field, errors in form.errors.items():
            for error in errors:
                if field == '__all__':
                    messages.error(self.request, error)
                else:
                    messages.error(self.request, f"{form.fields[field].label}: {error}")
        
        return super().form_invalid(form)
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # nothing exotic required but helpful:
        ctx['branding'] = getattr(self.request, 'branding', None)  # optional
        ctx['profile_sections'] = [
        {
            "id": "basic",
            "title": "Basic & Branding",
            "summary": "Name, short bio and brand color/logo",
            "fields": ["business_name", "bio", "logo", "brand_color"]
        },
        {
            "id": "expertise",
            "title": "Expertise & Services",
            "summary": "Specialties, certifications, services you offer",
            "fields": ["specializations", "certifications", "services_offered"]
        },
        {
            "id": "experience",
            "title": "Experience & Rates",
            "summary": "Years of experience, hourly rate, accepting clients",
            "fields": ["experience_years", "hourly_rate", "is_accepting_clients"]
        },
        {
            "id": "contact",
            "title": "Contact & Location",
            "summary": "Address, city and web/social links",
            "fields": ["address", "city", "website", "instagram"]
        },
    ]

        ctx['current_section_id'] = ctx['profile_sections'][0]['id']

    # If form bound with errors, open section containing the first error field
        form = ctx.get('form')
        if form and form.errors:
            error_fields = set(form.errors.keys())
            for sec in ctx['profile_sections']:
                if error_fields & set(sec['fields']):
                    ctx['current_section_id'] = sec['id']
                    break

        # keep current list of fields in context if needed in template
        ctx['profile_fields'] = [f for sec in ctx['profile_sections'] for f in sec['fields']]

        return ctx
    
    def dispatch(self, request, *args, **kwargs):
        # Redirect if profile already exists
        if hasattr(request.user, 'trainer_profile') and request.user.is_active_subscription:
            return redirect('trainers:dashboard')
        return super().dispatch(request, *args, **kwargs)
        

class TrainerProfileEditView(LoginRequiredMixin,TrainerRequiredMixin,UpdateView):
    model = TrainerProfile
    form_class = TrainerProfileForm
    template_name = 'trainers/setup_profile.html'   # reuse create template
    success_url = reverse_lazy('trainers:dashboard')

    def get_object(self, queryset=None):
        profile, created = TrainerProfile.objects.get_or_create(user=self.request.user)
        return profile

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # replicate same sections & current_section logic as in CreateView
        ctx['profile_sections'] = [
            {"id": "basic", "title": "Basic & Branding", "fields": ["business_name","bio","logo","brand_color","hourly_rate"]},
            {"id": "expertise", "title": "Expertise & Services", "fields": ["specializations","certifications","services_offered"]},
            {"id": "experience", "title": "Experience & Rates", "fields": ["experience_years","is_accepting_clients"]},
            {"id": "contact", "title": "Contact & Location", "fields": ["address","city","website","instagram"]},
        ]
        ctx['current_section_id'] = ctx['profile_sections'][0]['id']
        form = ctx.get('form')
        if form and form.errors:
            error_fields = set(form.errors.keys())
            for sec in ctx['profile_sections']:
                if error_fields & set(sec['fields']):
                    ctx['current_section_id'] = sec['id']
                    break
        return ctx

    def form_valid(self, form):
        messages.success(self.request, "Profile updated.")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        # Highlight which section to open
        self.extra_context = self.get_context_data(form=form)
        
        # Add error messages for the user
        for field, errors in form.errors.items():
            for error in errors:
                if field == '__all__':
                    messages.error(self.request, error)
                else:
                    messages.error(self.request, f"{form.fields[field].label}: {error}")
        
        return super().form_invalid(form)
    
class ClientListView(LoginRequiredMixin,TrainerRequiredMixin,SubscriptionRequiredMixin, ListView):
    model = ClientProfile
    template_name = 'trainers/client_list.html'
    context_object_name = 'clients'
    paginate_by = 20
    
    def get_queryset(self):
        trainer_profile = get_object_or_404(TrainerProfile, user=self.request.user)
        queryset = trainer_profile.clients.all()
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(user__email__icontains=search)
            )
        
        return queryset.order_by('-created_at')

class AddClientView(LoginRequiredMixin,TrainerRequiredMixin,SubscriptionRequiredMixin, PackageLimitMixin, CreateView):
    model = ClientProfile
    form_class = ClientInviteForm
    template_name = 'trainers/add_client.html'
    success_url = reverse_lazy('trainers:client_list')
    limit_type = 'max_clients'
    
    def form_valid(self, form):
        trainer_profile = get_object_or_404(TrainerProfile, user=self.request.user)
        form.instance.trainer = trainer_profile
        messages.success(self.request, 'Client invitation sent successfully!')
        return super().form_valid(form)

class ClientUpdateView(LoginRequiredMixin,TrainerRequiredMixin,SubscriptionRequiredMixin, UpdateView):
    model = ClientProfile
    form_class = ClientProfileUpdateForm
    template_name = 'trainers/update_client.html'
    success_url = reverse_lazy('trainers:client_list')
    
    def get_queryset(self):
        """
        Ensure the trainer can only update their own clients.
        """
        trainer_profile = get_object_or_404(TrainerProfile, user=self.request.user)
        return ClientProfile.objects.filter(trainer=trainer_profile)
    
    def form_valid(self, form):
        days = form.cleaned_data['preferred_workout_days']  # e.g. ['Mon','Wed']
        form.instance.preferred_workout_days = ", ".join(days)
        messages.success(self.request, 'Client profile updated successfully!')
        return super().form_valid(form)
    
class ClientDetailView(LoginRequiredMixin,TrainerRequiredMixin,SubscriptionRequiredMixin, DetailView):
    model = ClientProfile
    template_name = 'trainers/client_detail.html'
    context_object_name = 'client'
    
    def get_queryset(self):
        trainer_profile = get_object_or_404(TrainerProfile, user=self.request.user)
        return trainer_profile.clients.all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client = self.get_object()

        # Get recent progress
        recent_progress = ClientProgress.objects.filter(client=client).order_by('-date')[:10]

        labels = [p.date.strftime("%b %d") for p in recent_progress]
        adherence_scores = [p.adherence_score for p in recent_progress]
        weights = [float(p.current_weight) if p.current_weight else None for p in recent_progress]
        sleep_hours = [float(p.sleep_hours) if p.sleep_hours else None for p in recent_progress]
        energy_levels = [p.energy_level if p.energy_level else None for p in recent_progress]
        stress_levels = [p.stress_level if p.stress_level else None for p in recent_progress]

        # Radar: take first and last entry for comparison
        first_entry, last_entry = None, None
        if recent_progress:
            first_entry = recent_progress[0]
            last_entry = recent_progress[len(recent_progress)-1]

        radar_labels = ["Chest", "Waist", "Hip", "Arm", "Thigh"]
        radar_first = [
            float(first_entry.chest_measurement or 0),
            float(first_entry.waist_measurement or 0),
            float(first_entry.hip_measurement or 0),
            float(first_entry.arm_measurement or 0),
            float(first_entry.thigh_measurement or 0),
        ] if first_entry else []

        radar_last = [
            float(last_entry.chest_measurement or 0),
            float(last_entry.waist_measurement or 0),
            float(last_entry.hip_measurement or 0),
            float(last_entry.arm_measurement or 0),
            float(last_entry.thigh_measurement or 0),
        ] if last_entry else []

        # Use json.dumps to make everything safe for JavaScript
        context.update({
            'chart_labels': json.dumps(labels),
            'chart_adherence': json.dumps(adherence_scores),
            'chart_weights': json.dumps(weights),
            'chart_sleep': json.dumps(sleep_hours),
            'chart_energy': json.dumps(energy_levels),
            'chart_stress': json.dumps(stress_levels),
            'radar_labels': json.dumps(radar_labels),
            'radar_first': json.dumps(radar_first),
            'radar_last': json.dumps(radar_last),
            'recent_progress': recent_progress
        })
        return context



class ClientDeleteView(LoginRequiredMixin,TrainerRequiredMixin,SubscriptionRequiredMixin,DeleteView):
    model = ClientProfile
    template_name = 'trainers/delete_client.html'  
    success_url = reverse_lazy('trainers:client_list')  
    def get_queryset(self):
        queryset = super().get_queryset()
        trainer_clients = self.request.user.trainer_profile.clients.filter(id=self.kwargs['pk'])
        user_ids = trainer_clients.values_list('user_id', flat=True)
        return queryset.filter(user_id__in=user_ids)
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Client deleted successfully!')
        return super().delete(request, *args, **kwargs)


class AnalyticsView(LoginRequiredMixin,TrainerRequiredMixin,SubscriptionRequiredMixin, TemplateView):
    template_name = 'trainers/analytics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        trainer_profile = get_object_or_404(TrainerProfile, user=self.request.user)
        
        # Analytics data
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        context.update({
            'trainer_profile': trainer_profile,
            'monthly_progress_entries': ClientProgress.objects.filter(
                client__trainer=trainer_profile,
                date__gte=thirty_days_ago
            ).count(),
            'client_adherence_avg': ClientProgress.objects.filter(
    client__trainer=trainer_profile,
    date__gte=thirty_days_ago
).aggregate(
    avg_workout=Avg('workout_completed'),
    avg_meal=Avg('meal_plan_followed')
),

        })
        
        return context

class SettingsView(LoginRequiredMixin,TrainerRequiredMixin,SubscriptionRequiredMixin, UpdateView):
    model = TrainerProfile
    fields = ['package', 'hourly_rate', 'is_accepting_clients']
    template_name = 'trainers/settings.html'
    success_url = reverse_lazy('trainers:settings')
    
    def get_object(self):
        return get_object_or_404(TrainerProfile, user=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Settings updated successfully!')
        return super().form_valid(form)