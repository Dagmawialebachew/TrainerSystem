import json
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import TemplateView, UpdateView, CreateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from django.db import transaction
from apps.accounts.forms import ProfileUpdateForm
from apps.core.mixins import ClientRequiredMixin
from apps.workouts.models import WorkoutPlan
from apps.nutrition.models import MealPlan
from apps.progress.models import ClientProgress
from apps.messaging.models import EngagementMessage
from apps.trainers.models import TrainerProfile
from .models import ClientProfile
from .forms import ClientProfileUpdateForm, ProgressLogForm, ClientEditProfileUpdateForm
from datetime import datetime


class ClientDashboardView(LoginRequiredMixin, ClientRequiredMixin, TemplateView):
    template_name = 'clients/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client_profile, _ = ClientProfile.objects.get_or_create(user=self.request.user)
        client_progress = ClientProgress.objects.filter(client=client_profile)
        
        ##Charts
        recent_progress = client_progress.order_by('date')
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

        today = timezone.localdate()

        # Active plans
        active_workout_plan = WorkoutPlan.objects.filter(client=client_profile, is_active=True).first()
        active_meal_plan = MealPlan.objects.filter(client=client_profile, is_active=True).first()

        # Prepare plans for template: (plan, url_name, color)
        plans = [
            (active_workout_plan, 'clients:workout_plan', 'blue'),
            (active_meal_plan, 'clients:meal_plan', 'orange')
        ]
        context['plans'] = plans

        # Today's progress items
        today_progress = client_progress.filter(date = today).order_by('-created_at').first()
        progress_items = []
        if today_progress:
            progress_items = [
                ('workout', "Workout", today_progress.workout_completed),
                ('meal', "Meal Plan", today_progress.meal_plan_followed),
            ]
        context['progress_items'] = progress_items
        stats_cards = [
                {
                "title": "Workouts Completed", 
                "value": client_progress.filter(workout_completed=True).count(), 
                "color": "bg-blue-600", 
                "icon": "check-circle"
                },
                {
                "title": "Active Plans", 
                "value": MealPlan.objects.filter(client=client_profile, is_active=True).count() + WorkoutPlan.objects.filter(client=client_profile, is_active=True).count(),
                "color": "bg-green-600", 
                "icon": "clipboard-list"
                },
                {
                "title": "Unread Messages", 
                "value": EngagementMessage.objects.filter(client=client_profile, is_read=False).count(),
                "color": "bg-yellow-600", 
                "icon": "envelope"
                },
                {
                "title": "Progress %", 
                "value": f"{(client_progress.filter(workout_completed=True).count() / max(client_progress.count(), 1)) * 100:.0f}%",
                "color": "bg-purple-600", 
                "icon": "chart-pie"
                }
        ]
    

        # Recent messages
        recent_messages = EngagementMessage.objects.filter(client=client_profile).order_by('-created_at')[:5]

        # Add other context
        context.update({
            'client_profile': client_profile,
            'active_workout_plan': active_workout_plan,
            'active_meal_plan': active_meal_plan,
            'today_progress': today_progress,
            'recent_messages': recent_messages,
            'today': today,
            'stats_cards': stats_cards,
        })

        return context


class ClientSetupProfileView(LoginRequiredMixin, ClientRequiredMixin, CreateView):
    model = ClientProfile
    form_class = ClientProfileUpdateForm
    template_name = 'clients/setup_profile.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Redirect if profile already exists
        if hasattr(request.user, 'client_profile'):
            messages.info(request, "You have already completed your profile.")
            return redirect('clients:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        trainers = TrainerProfile.objects.all().filter(user__is_active_subscription = True) 
        context.update({
            'trainers': trainers
        })
        context["step_titles"] = ["Trainer", "Info", "Prefs"]
        form = context.get("form")
        if form and form.errors:
            errors = set(form.errors.keys())
            pref_fields = {"preferred_workout_days", "workout_duration_preference"}
            if "trainer" in errors:
                context["current_step"] = 0
            elif errors & pref_fields:
                context["current_step"] = 2
            else:
                context["current_step"] = 1
        else:
            context["current_step"] = 0
            
        
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Pass queryset for trainers
        form.fields['trainer'].queryset = TrainerProfile.objects.filter()
        return form

    def form_valid(self, form):
        trainer_id = self.request.POST.get('trainer')
        if not trainer_id:
            messages.error(self.request, "Please select a trainer to continue.")
            return self.form_invalid(form)

        trainer = get_object_or_404(TrainerProfile, id=trainer_id)
        form.instance.user = self.request.user
        form.instance.trainer = trainer

        response = super().form_valid(form)
        messages.success(self.request, "Profile setup completed successfully!")
        return redirect('clients:dashboard')
    
class ClientEditProfileView(LoginRequiredMixin, UpdateView):
    template_name = "clients/edit_profile.html"
    form_class = ClientEditProfileUpdateForm
    success_url_name = "clients:dashboard"

    def get_client_profile(self):
        profile, _ = ClientProfile.objects.get_or_create(user=self.request.user)
        return profile
    

    def get(self, request, *args, **kwargs):
        user = request.user
        client_profile = self.get_client_profile()
        context = {
            "profile_form": ProfileUpdateForm(instance=user),
            "client_form": ClientEditProfileUpdateForm(instance=client_profile),
            "current_profile_picture_url": user.profile_picture.url if getattr(user, "profile_picture", None) and user.profile_picture else "",
            "has_profile_picture": bool(getattr(user, "profile_picture", None) and user.profile_picture),
        }
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        user = request.user
        client_profile = self.get_client_profile()
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=user)
        client_form = ClientEditProfileUpdateForm(request.POST, instance=client_profile)
    
        if profile_form.is_valid() and client_form.is_valid():
            with transaction.atomic():
                days = client_form.cleaned_data['preferred_workout_days']  # e.g. ['Mon','Wed']
                client_form.instance.preferred_workout_days = ", ".join(days)
                profile_form.save()
                client_form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect(self.success_url_name)
        else:
          for form in [profile_form, client_form]:
            for field, errors in form.errors.items():
                for error in errors:
                    # You can format this however you like
                    messages.error(request, f"{field}: {error}")

        context = {
            "profile_form": profile_form,
            "client_form": client_form,
            "current_profile_picture_url": user.profile_picture.url if getattr(user, "profile_picture", None) and user.profile_picture else "",
            "has_profile_picture": bool(getattr(user, "profile_picture", None) and user.profile_picture),
        }
        return self.render_to_response(context)

class WorkoutPlanView(LoginRequiredMixin, ClientRequiredMixin, TemplateView):
    template_name = 'clients/workout_plan.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client_profile = get_object_or_404(ClientProfile, user=self.request.user)
        
        active_plan = WorkoutPlan.objects.filter(
            client=client_profile, is_active=True
        )
        
        
        context.update({
            'client_profile': client_profile,
            'workout_plans': active_plan,
        })
        
        return context
    
class WorkoutPlanDetailView(LoginRequiredMixin, ClientRequiredMixin, DetailView):
    model = WorkoutPlan
    template_name = "clients/workout_plan_detail.html"
    context_object_name = "workout_plan"

    def get_queryset(self):
        # Restrict plans to the logged-in client
        client_profile = get_object_or_404(ClientProfile, user=self.request.user)
        return WorkoutPlan.objects.filter(client=client_profile)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        workout_plan = self.get_object()

        # Add formatted structure

        
        context['workout_structure'] = workout_plan.workout_structure if isinstance(workout_plan.workout_structure, list) else []
        print('this is the map passed',context['workout_structure'])

        return context
    
class MealPlanView(LoginRequiredMixin, ClientRequiredMixin, TemplateView):
    template_name = "clients/meal_plan.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client_profile = get_object_or_404(ClientProfile, user=self.request.user)
        
        active_plan = MealPlan.objects.filter(
            client=client_profile, is_active=True
        )
        
        context.update({
            'client_profile': client_profile,
            'meal_plans': active_plan,
        })
        print('this is the meal plan passed',context['meal_plans'])
        
        return context


class MealPlanDetailView(LoginRequiredMixin, ClientRequiredMixin, DetailView):
    model = MealPlan
    template_name = 'clients/meal_plan_detail.html'
    context_object_name = 'meal_plan'

    def get_queryset(self):
        client_profile = self.request.user.client_profile
        return MealPlan.objects.filter(client=client_profile)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ensure meal_structure is a dict
        meal_structure = self.object.meal_structure
        if isinstance(meal_structure, str):
            try:
                meal_structure = json.loads(meal_structure)
            except json.JSONDecodeError:
                meal_structure = {}
        context['meal_structure'] = meal_structure
        daily_totals = {}
        for day, meals in meal_structure.items():
            total_protein = 0
            total_carbs = 0
            total_fat = 0
            for meal_items in meals.values():
                for item in meal_items:
                    total_protein += item.get('protein', 0)
                    total_carbs += item.get('carbs', 0)
                    total_fat += item.get('fat', 0)
            daily_totals[day] = {
                'protein': total_protein,
                'carbs': total_carbs,
                'fat': total_fat
            }
        context['daily_totals'] = daily_totals
        print('daily_total', daily_totals)
        
        # Optional: pass week_days and meals if you want to keep same structure as form
        context['week_days'] = list(meal_structure.keys()) if meal_structure else []
        context['current_day'] = datetime.today().strftime('%A') 
        print('current day is: ', context['current_day'])
        context['meals'] = []
        if context['week_days']:
            first_day = context['week_days'][0]
            context['meal_plans'] = list(meal_structure[first_day].keys()) if meal_structure[first_day] else []

        return context

class ProgressView(LoginRequiredMixin, ClientRequiredMixin, ListView):
    model = ClientProgress
    template_name = 'clients/progress_list.html'
    context_object_name = 'progress_entries'
    paginate_by = 30
    ordering = ['-date']

    def get_queryset(self):
        # 1) Base queryset: only this client’s progress
        client = get_object_or_404(ClientProfile, user=self.request.user)
        qs = ClientProgress.objects.filter(client=client).order_by('date')

        # 2) Apply GET filters
        start = self.request.GET.get('start')
        end   = self.request.GET.get('end')
        energy = self.request.GET.get('energy')      # '1','2','3'
        workout = self.request.GET.get('workout')    # 'yes','no'

        if start:
            try:
                qs = qs.filter(date__gte=start)
            except ValueError:
                pass
        if end:
            try:
                qs = qs.filter(date__lte=end)
            except ValueError:
                pass

        if energy in {'1','2','3', '4','5'}:
            qs = qs.filter(energy_level=int(energy))

        if workout in {'yes','no'}:
            qs = qs.filter(workout_completed = (workout == 'yes'))

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client = get_object_or_404(ClientProfile, user=self.request.user)


        # 3) Pull the full filtered queryset for stats + trends
        full_qs = self.get_queryset().order_by('date')
        entries = list(full_qs)

        # 4) Build serializable dicts + text snippet
        serialized = []
        adherence_scores = []
        for e in entries:
            notes = e.notes or ''
            workout = 1 if e.workout_completed else 0
            meal = 1 if e.meal_plan_followed else 0
            adherence_score = (workout + meal) / 2 * 100
            adherence_scores.append(adherence_score)
            snippet = notes[:80] + ('…' if len(notes) > 80 else '')
            serialized.append({
                'date': e.date.strftime('%Y-%m-%d'),
                'current_weight': float(e.current_weight) if e.current_weight else None,
                'workout_completed': e.workout_completed,
                'meal_plan_followed': e.meal_plan_followed,
                'energy_level': e.energy_level,
                'stress_level': e.stress_level,
                'sleep_hours': e.sleep_hours,
                'notes': notes,
                'snippet': snippet,
                'pk': e.pk,
                'progress_photo': e.progress_photo,
                'trainer_feedback': e.trainer_feedback,
                'chest_measurement': e.chest_measurement,
                'waist_measurement': e.waist_measurement,
                'hip_measurement': e.hip_measurement,
                'arm_measurement': e.arm_measurement,
                'thigh_measurement': e.thigh_measurement,
                'adherence_score': e.adherence_score,
                
                })
            
            

        average_adherence = sum(adherence_scores) / len(adherence_scores) if adherence_scores else 0

        # 5) Compute stats
        total = len(serialized)
        done_wk = sum(1 for x in serialized if x['workout_completed'])
        done_meals = sum(1 for x in serialized if x['meal_plan_followed'])
        weights = [x['current_weight'] for x in serialized if x['current_weight'] is not None]
        avg_w = round(sum(weights) / len(weights), 1) if weights else 0

        # 6) Chart.js datasets
        weight_trend = [
            {'x': x['date'], 'y': x['current_weight']}
            for x in serialized if x['current_weight'] is not None
        ]
        energy_trend = [
            {'x': x['date'], 'y': x['energy_level']}
            for x in serialized if x['energy_level'] is not None
        ]
        
        sleep_trend = [
    {'x': x['date'], 'y': float(x['sleep_hours'])}
    for x in serialized if x['sleep_hours'] is not None
]
        stress_trend = [
            {'x': x['date'], 'y': x['stress_level']}
            for x in serialized if x['stress_level'] is not None
        ]

        # 7) Expose filter state back to template
        context.update({
            'filter_start': self.request.GET.get('start',''),
            'filter_end':   self.request.GET.get('end',''),
             "client_profile": client,  # <-- important for reversing URLs

            'filter_energy': self.request.GET.get('energy',''),
            'filter_workout': self.request.GET.get('workout',''),
            'filter_q':     self.request.GET.get('q',''),  # if you add a search box

            # serial + paginated entries
            'progress_entries': serialized,  # use this instead of the model instances
            'total_entries': total,
            'workouts_done': done_wk,
            'average_adherence': f'{round(average_adherence,1)}%',
            'meals_followed': done_meals,
            'avg_weight': avg_w,

            # chart data for Chart.js
            'weight_trend': weight_trend,
            'energy_trend': energy_trend,
            'sleep_trend': sleep_trend,
            'stress_trend': stress_trend,
            'labels': ''
        })
        return context

class ProgressDetailView(LoginRequiredMixin, ClientRequiredMixin, DetailView):
    model = ClientProgress
    template_name = "progress/progress_detail.html"
    context_object_name = "progress"

    def get_queryset(self):
        return ClientProgress.objects.filter(
            client=self.request.user.client_profile
        )
        
class LogProgressView(LoginRequiredMixin, ClientRequiredMixin, CreateView):
    model = ClientProgress
    form_class = ProgressLogForm
    template_name = 'progress/add_progress.html'
    success_url = reverse_lazy('clients:log_progress')
    
    def form_valid(self, form):
        client_profile = get_object_or_404(ClientProfile, user=self.request.user)
        form.instance.client = client_profile
        messages.success(self.request, 'Progress logged successfully!')
        return super().form_valid(form)

class MessagesView(LoginRequiredMixin, ClientRequiredMixin, ListView):
    model = EngagementMessage
    template_name = 'clients/messages.html'
    context_object_name = 'messages'
    paginate_by = 20
    
    def get_queryset(self):
        client_profile = get_object_or_404(ClientProfile, user=self.request.user)
        return EngagementMessage.objects.filter(
            client=client_profile
        ).order_by('-created_at')