from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Avg, Count
from django.utils import timezone
from datetime import datetime, timedelta

from apps.core.mixins import TrainerRequiredMixin, SubscriptionRequiredMixin, TrainerOwnedMixin
from apps.trainers.models import TrainerProfile
from apps.clients.models import ClientProfile
from .models import ClientProgress, ProgressGoal
from .forms import ProgressGoalForm, ClientProgressForm

class ProgressOverviewView(LoginRequiredMixin, TrainerRequiredMixin, SubscriptionRequiredMixin, TemplateView):
    template_name = 'progress/overview.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        trainer_profile = get_object_or_404(TrainerProfile, user=self.request.user)
        
        # Get progress statistics
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        
        progress_stats = ClientProgress.objects.filter(
            client__trainer=trainer_profile,
            date__gte=thirty_days_ago
        ).aggregate(
            avg_workout_adherence=Avg('workout_completed'),
            avg_meal_adherence=Avg('meal_plan_followed'),
            total_entries=Count('id')
        )
        
        # Recent progress entries
        recent_progress = ClientProgress.objects.filter(
            client__trainer=trainer_profile
        ).order_by('-date')[:20]
        
        
        context.update({
            'trainer_profile': trainer_profile,
            'progress_stats': progress_stats,
            'recent_progress': recent_progress,
        })
        
        return context
    

class CreateProgressView(LoginRequiredMixin, CreateView):
    model = ClientProgress
    form_class = ClientProgressForm
    template_name = 'progress/add_progress.html'

    def dispatch(self, request, *args, **kwargs):
        self.client_profile = None
        self.trainer_profile = None

        # Trainer logic (keep your existing flow)
        if hasattr(request.user, 'trainer_profile') and self.request.user.is_trainer:
            self.trainer_profile = get_object_or_404(TrainerProfile, user=request.user)
            self.client_pk = kwargs.get('client_pk')
            if self.client_pk:
                try:
                    self.client_profile = ClientProfile.objects.get(
                        pk=self.client_pk, trainer=self.trainer_profile
                    )
                except ClientProfile.DoesNotExist:
                    messages.error(request, "Selected client does not exist or is not assigned to you.")
                    return redirect('progress:add_progress')

        # Client logic
        elif hasattr(request.user, 'client_profile') and self.request.user.is_client:
            self.client_profile = request.user.client_profile
            
      
        # Neither trainer nor client
        

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        # Trainer selecting client
        if self.trainer_profile and not getattr(self, 'client_pk', None):
            clients = ClientProfile.objects.filter(trainer=self.trainer_profile, is_active=True)
            if not clients.exists():
                messages.error(request, "No active clients available.")
            return render(request, 'progress/select_client.html', {'clients': clients})
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # Trainer selecting client
        if self.trainer_profile and not getattr(self, 'client_pk', None):
            selected_pk = request.POST.get('client_pk')
            clients = ClientProfile.objects.filter(trainer=self.trainer_profile, is_active=True)
            if not selected_pk:
                messages.error(request, "Please select a client to continue.")
                return render(request, 'progress/select_client.html', {'clients': clients})

            try:
                self.client_profile = clients.get(pk=selected_pk)
                return redirect('progress:add_progress', client_pk=self.client_profile.pk)
            except ClientProfile.DoesNotExist:
                messages.error(request, "Selected client is not valid.")
                return render(request, 'progress/select_client.html', {'clients': clients})

        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.client = self.client_profile
        messages.success(self.request, "Progress entry added successfully!")
        return super().form_valid(form)

    def form_invalid(self, form):
        error_messages = []
        for field, errors in form.errors.items():
            field_label = form.fields[field].label if field in form.fields else field
            for error in errors:
                error_messages.append(f"{field_label}: {error}")
        messages.error(self.request, " | ".join(error_messages))
        return super().form_invalid(form)

    def get_success_url(self):
        # Client goes to dashboard, trainer goes to client progress
        if hasattr(self.request.user, 'client_profile'):
            return reverse_lazy('clients:dashboard')
        return reverse_lazy('progress:client_progress', kwargs={'client_pk': self.client_profile.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['client'] = self.client_profile
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['client'] = self.client_profile
        return kwargs


class ProgressListView(LoginRequiredMixin, TrainerRequiredMixin, SubscriptionRequiredMixin, TrainerOwnedMixin, ListView):
    model = ClientProgress
    template_name = 'progress/progress_list.html'
    context_object_name = 'progress_list'
    paginate_by = 10

    def get_queryset(self):
        self.trainer_profile = get_object_or_404(TrainerProfile, user=self.request.user)
        queryset = (
            ClientProgress.objects.select_related('client', 'client__user')
            .filter(client__trainer=self.trainer_profile)
            .order_by('-date')
        )

        # Filters
        client_query = self.request.GET.get('client')
        date_query = self.request.GET.get('date')

        if client_query:
            queryset = queryset.filter(client__user__first_name__icontains=client_query)

        if date_query:
            queryset = queryset.filter(date=date_query)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        recent_progress = ClientProgress.objects.filter(
            client__trainer=self.trainer_profile
          
        ).order_by('-date')

        stats = recent_progress.aggregate(
            avg_workout_adherence=Avg('workout_completed'),
            avg_meal_adherence=Avg('meal_plan_followed'),
            total_entries=Count('id')
        )

        context.update({
            'trainer_profile': self.trainer_profile,
            'progress_stats': stats,
            'filters': {
                'client': self.request.GET.get('client', ''),
                'date': self.request.GET.get('date', ''),
            }
        })
        context['client_profiles'] = ClientProfile.objects.filter(trainer=self.trainer_profile)

        return context
    
class DeleteProgressView(LoginRequiredMixin, TrainerRequiredMixin, SubscriptionRequiredMixin,DeleteView):
    model = ClientProgress
    template_name = 'progress/delete_progress.html'  # This is your confirmation page
    success_url = reverse_lazy('progress:list')  # Redirect after deletion

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(client__trainer=self.request.user.trainer_profile)

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Progress deleted successfully!')
        return super().delete(request, *args, **kwargs)

class GoalListView(LoginRequiredMixin, TrainerRequiredMixin, SubscriptionRequiredMixin, TrainerOwnedMixin, ListView):
    model = ProgressGoal
    template_name = 'progress/goal_list.html'
    context_object_name = 'goals'
    paginate_by = 10

class CreateGoalView(LoginRequiredMixin, TrainerRequiredMixin, SubscriptionRequiredMixin, CreateView):
    model = ProgressGoal
    form_class = ProgressGoalForm
    template_name = 'progress/create_goal.html'
    success_url = reverse_lazy('progress:goal_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['trainer'] = get_object_or_404(TrainerProfile, user=self.request.user)
        return kwargs
    
    def form_valid(self, form):
        trainer_profile = get_object_or_404(TrainerProfile, user=self.request.user)
        form.instance.trainer = trainer_profile
        messages.success(self.request, 'Goal created successfully!')
        return super().form_valid(form)

class GoalDetailView(LoginRequiredMixin, TrainerRequiredMixin, SubscriptionRequiredMixin, TrainerOwnedMixin, DetailView):
    model = ProgressGoal
    template_name = 'progress/goal_detail.html'
    context_object_name = 'goal'

class EditGoalView(LoginRequiredMixin, TrainerRequiredMixin, SubscriptionRequiredMixin, TrainerOwnedMixin, UpdateView):
    model = ProgressGoal
    form_class = ProgressGoalForm
    template_name = 'progress/edit_goal.html'
    success_url = reverse_lazy('progress:goal_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['trainer'] = get_object_or_404(TrainerProfile, user=self.request.user)
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, 'Goal updated successfully!')
        return super().form_valid(form)
    
    
class DeleteGoalView(LoginRequiredMixin, TrainerRequiredMixin, SubscriptionRequiredMixin, DeleteView):
    model = ProgressGoal
    template_name = 'progress/delete_goal.html'  # This is your confirmation page
    success_url = reverse_lazy('progress:list')  # Redirect after deletion

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(client__trainer=self.request.user.trainer_profile)

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Goal deleted successfully!')
        return super().delete(request, *args, **kwargs)


class ClientProgressView(LoginRequiredMixin, TemplateView):
    template_name = 'progress/client_progress.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request
        user = request.user

        # Role logic
        is_trainer = getattr(user, "is_trainer", False) or user.groups.filter(name="Trainer").exists()

        # Get client profile
        if is_trainer:
            trainer_profile = get_object_or_404(TrainerProfile, user=user)
            client_profile = get_object_or_404(ClientProfile, pk=kwargs['client_pk'], trainer=trainer_profile)
        else:
            client_profile = get_object_or_404(ClientProfile, user=user)

        # Filters via GET
        start = request.GET.get("start")
        end = request.GET.get("end")
        energy = request.GET.get("energy")
        workout = request.GET.get("workout")
        goal_type = request.GET.get("goal_type")

        entries_qs = ClientProgress.objects.filter(client=client_profile).order_by("date")

        # Apply filters
        if start:
            try:
                entries_qs = entries_qs.filter(date__gte=datetime.fromisoformat(start).date())
            except ValueError:
                pass
        if end:
            try:
                entries_qs = entries_qs.filter(date__lte=datetime.fromisoformat(end).date())
            except ValueError:
                pass
        if energy in {"1", "2", "3"}:
            entries_qs = entries_qs.filter(energy_level=int(energy))
        if workout in {"yes", "no"}:
            entries_qs = entries_qs.filter(workout_completed=(workout == "yes"))
            
            
        #for each entry deatils
        
        # In your view
        entry_pk = kwargs.get("entry_pk") 
        entry_obj = get_object_or_404(ClientProgress, pk=entry_pk, client=client_profile)

        # Build progress_entry dictionary for just this one entry
        notes = entry_obj.notes or ''
        workout = 1 if entry_obj.workout_completed else 0
        meal = 1 if entry_obj.meal_plan_followed else 0
        adherence_score = (workout + meal) / 2 * 100

        entry_detail = {
            "date": entry_obj.date.strftime("%Y-%m-%d"),
            "workout_completed": entry_obj.workout_completed,
            "meal_plan_followed": entry_obj.meal_plan_followed,
            "current_weight": float(entry_obj.current_weight) if entry_obj.current_weight else None,
            "energy_level": entry_obj.energy_level,
            "stress_level": entry_obj.stress_level,
            "sleep_hours": entry_obj.sleep_hours,
            "notes": notes,
            "snippet": notes[:80] + ('…' if len(notes) > 80 else ''),
            "pk": entry_obj.pk,
            "progress_photo": entry_obj.progress_photo,
            "trainer_feedback": entry_obj.trainer_feedback,
            "chest_measurement": entry_obj.chest_measurement,
            "waist_measurement": entry_obj.waist_measurement,
            "hip_measurement": entry_obj.hip_measurement,
            "arm_measurement": entry_obj.arm_measurement,
            "thigh_measurement": entry_obj.thigh_measurement,
            "adherence_score": adherence_score,
            "client_profile": client_profile, 

        }

        context.update({
            "entry_detail": entry_detail
        })


        # Serialize entries
        adherence_scores = []
        progress_entries = []
        for entry in entries_qs:
            notes = entry.notes or ''
            workout = 1 if entry.workout_completed else 0
            meal = 1 if entry.meal_plan_followed else 0
            adherence_score = (workout + meal) / 2 * 100
            adherence_scores.append(adherence_score)
            snippet = notes[:80] + ('…' if len(notes) > 80 else '')
            progress_entries.append({
                "date": entry.date.strftime("%Y-%m-%d"),
                "workout_completed": entry.workout_completed,
                "meal_plan_followed": entry.meal_plan_followed,
                "current_weight": float(entry.current_weight) if entry.current_weight else None,

                'energy_level': entry.energy_level,
                'stress_level': entry.stress_level,
                'sleep_hours': entry.sleep_hours,
                'notes': notes,
                'snippet': snippet,
                'pk': entry.pk,
                'progress_photo': entry.progress_photo,
                'trainer_feedback': entry.trainer_feedback,
                'chest_measurement': entry.chest_measurement,
                'waist_measurement': entry.waist_measurement,
                'hip_measurement': entry.hip_measurement,
                'arm_measurement': entry.arm_measurement,
                'thigh_measurement': entry.thigh_measurement,
                'adherence_score': entry.adherence_score,
            })
            
        average_adherence = sum(adherence_scores) / len(adherence_scores) if adherence_scores else 0


        # Trend data
        weight_trend = [{"x": e["date"], "y": e["current_weight"]} for e in progress_entries if e["current_weight"]]
        energy_trend = [{"x": e["date"], "y": e["energy_level"]} for e in progress_entries if e["energy_level"]]
        workout_trend = [{"x": e["date"], "y": 1 if e["workout_completed"] else 0} for e in progress_entries]

        # Goals
        goals_qs = ProgressGoal.objects.filter(client=client_profile).order_by("-created_at")
        if goal_type:
            goals_qs = goals_qs.filter(goal_type=goal_type)

        client_goals = []
        for goal in goals_qs:
            pct = 0.0
            try:
                if goal.target_value:
                    pct = min(100.0, (float(goal.current_value) / float(goal.target_value)) * 100.0)
            except Exception:
                pass
            client_goals.append({
                "title": goal.title,
                "goal_type": goal.goal_type,
                "unit": goal.unit,
                "target_value": goal.target_value,
                "current_value": goal.current_value,
                "progress_percentage": round(pct, 1),
                "created_at": goal.created_at.strftime("%Y-%m-%d"),
                "description": goal.description or "",
            })

        # Stats
        total_entries = len(progress_entries)
        workouts_done = sum(1 for e in progress_entries if e["workout_completed"])
        meals_followed = sum(1 for e in progress_entries if e["meal_plan_followed"])
        avg_weight = round(
            sum(e["current_weight"] for e in progress_entries if e["current_weight"]) /
            max(1, sum(1 for e in progress_entries if e["current_weight"])), 1
        )

        # Streak logic
        today = timezone.localdate()
        streak = 0
        dates_done = {e["date"] for e in progress_entries if e["workout_completed"]}
        cursor = today
        while cursor.strftime("%Y-%m-%d") in dates_done:
            streak += 1
            cursor -= timezone.timedelta(days=1)

        context.update({
            "client_profile": client_profile,
            "is_trainer": is_trainer,

            # Filters
            "filter_start": start or "",
            "filter_end": end or "",
            "filter_energy": energy or "",
            "filter_workout": workout or "",
            "filter_goal_type": goal_type or "",

            # Data
            "progress_entries": progress_entries,
            "client_goals": client_goals,

            # Stats
            "total_entries": total_entries,
            "workouts_done": workouts_done,
            "meals_followed": meals_followed,
            "avg_weight": avg_weight,
            'average_adherence': f'{round(average_adherence,1)}%',
            "streak": streak,

            # Charts
            "weight_trend": weight_trend,
            "energy_trend": energy_trend,
            "workout_trend": workout_trend,
        })

        return context
    
    
    
    
#API ENDPOINTS


# progress/api_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Avg
from datetime import timedelta, date

from .models import ClientProgress
from apps.clients.models import ClientProfile
from .serializers import ClientProgressSummarySerializer
from django.utils.dateparse import parse_date
from apps.core.mixins import TrainerRequiredMixin
class ProgressOverviewAPIView(APIView, TrainerRequiredMixin):
    def get(self, request):
        client_id = request.query_params.get('client_id')
        start_date_str = request.query_params.get('start_date')
        start_date = parse_date(start_date_str) if isinstance(start_date_str, str) else None

        end_date_str = request.query_params.get('end_date')
        end_date = parse_date(end_date_str) if isinstance(end_date_str, str) else None
        limit = int(request.query_params.get('limit', 10))

        entries = ClientProgress.objects.filter(client__trainer = request.user.trainer_profile).select_related('client__user')
        def calculate_streak(entries):
            streak = 0
            today = date.today()
            for i in range(0, 30):
                check_date = today - timedelta(days=i)
                if entries.filter(date=check_date).exists():
                    streak += 1
                else:
                    break
            return streak

        if client_id:
            entries = entries.filter(client_id=client_id)
            streak = calculate_streak(entries.filter(client_id=client_id))
        elif not client_id:
                streak = None
        if start_date:
            entries = entries.filter(date__gte=start_date)
        if end_date:
            entries = entries.filter(date__lte=end_date)

        entries = entries.order_by('-date')
        
        total_entries = entries.count()
        total_clients = ClientProfile.objects.filter(trainer=request.user.trainer_profile).count()

        avg_workout = entries.filter(workout_completed=True).count() / total_entries * 100 if total_entries else 0
        avg_meal = entries.filter(meal_plan_followed=True).count() / total_entries * 100 if total_entries else 0

        # Adherence Trend (last 7 days)
        today = date.today()
        last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]
        adherence_labels = [d.strftime('%a') for d in last_7_days]
        workout_data, meal_data = [], []

        for d in last_7_days:
            day_entries = entries.filter(date=d)
            total_day = day_entries.count()
            workout_pct = day_entries.filter(workout_completed=True).count() / total_day * 100 if total_day else 0
            meal_pct = day_entries.filter(meal_plan_followed=True).count() / total_day * 100 if total_day else 0
            workout_data.append(round(workout_pct, 1))
            meal_data.append(round(meal_pct, 1))

        # Energy & Sleep Distribution (top 5 recent clients)
        recent_clients = entries.values('client__user__first_name').annotate(
            avg_energy=Avg('energy_level'),
            avg_sleep=Avg('sleep_hours')
        ).order_by('-avg_sleep')[:5]


        energy_sleep_labels = [c['client__user__first_name'] for c in recent_clients]
        energy_data = [round(c['avg_energy'], 1) if c['avg_energy'] else 0 for c in recent_clients]
        sleep_data = [round(c['avg_sleep'], 1) if c['avg_sleep'] else 0 for c in recent_clients]

        recent_progress = ClientProgressSummarySerializer(entries[:10], many=True).data
      

        return Response({
            "progress_stats": {
                "total_clients": total_clients,
                "avg_workout_adherence": round(avg_workout, 1),
                "avg_meal_adherence": round(avg_meal, 1),
                "total_entries": total_entries
            },
            "recent_progress": recent_progress,
            "adherence_labels": adherence_labels,
            "workout_data": workout_data,
            "meal_data": meal_data,
            "streak_days": streak,
            "energy_sleep_labels": energy_sleep_labels,
            "energy_data": energy_data,
            "sleep_data": sleep_data
        })
