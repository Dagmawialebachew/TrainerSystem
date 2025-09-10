import json
from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from apps.schedules.forms import WorkoutScheduleForm
from apps.schedules.models import WorkoutSchedule
from apps.trainers.models import TrainerProfile
from django.urls import reverse_lazy

from apps.core.mixins import TrainerRequiredMixin, SubscriptionRequiredMixin, TrainerOwnedMixin
from .models import WorkoutPlan, Exercise
from .forms import WorkoutPlanForm

class WorkoutPlanListView(LoginRequiredMixin, TrainerRequiredMixin, SubscriptionRequiredMixin, TrainerOwnedMixin, ListView):
    model = WorkoutPlan
    template_name = 'workouts/list.html'
    context_object_name = 'workout_plans'
    paginate_by = 10

from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

class CreateWorkoutPlanView(LoginRequiredMixin, TemplateView):
    template_name = 'workouts/create.html'
    success_url   = reverse_lazy('workouts:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # always pass days
        context['days'] = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        # add forms
        trainer = get_object_or_404(TrainerProfile, user=self.request.user)
        context['plan_form']  = kwargs.get("plan_form") or WorkoutPlanForm(trainer=trainer)
        context['sched_form'] = kwargs.get("sched_form") or WorkoutScheduleForm()

        return context

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        trainer    = get_object_or_404(TrainerProfile, user=request.user)
        plan_form  = WorkoutPlanForm(request.POST, trainer=trainer)
        sched_form = WorkoutScheduleForm(request.POST)

        if plan_form.is_valid() and sched_form.is_valid():
            # 1) Save the plan
            plan = plan_form.save(commit=False)
            plan.trainer = trainer
            plan.save()

            # 2) Save the schedule
            sched = sched_form.save(commit=False)
            sched.trainer      = trainer
            sched.client       = plan.client
            sched.workout_plan = plan
            sched.save()

            # 3) Auto-generate sessions
            sched.generate_sessions()

            messages.success(request, 'Workout plan & schedule created!')
            return redirect(plan.get_absolute_url())

        # If invalid → re-render with errors and days
        messages.error(request, 'Please fix the errors below.')
        return render(request, self.template_name, self.get_context_data(
            plan_form=plan_form,
            sched_form=sched_form
        ))
class WorkoutPlanDetailView(LoginRequiredMixin,TrainerOwnedMixin, DetailView):
    model = WorkoutPlan
    template_name = 'workouts/detail.html'
    context_object_name = 'workout_plan'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        workout_plan = self.get_object()

        # Add formatted structure
        context['workout_structure'] = workout_plan.formatted_structure

        # Optional: preload exercises by name for richer display
        all_exercises = Exercise.objects.filter(is_active=True)
        exercise_map = {e.name.lower(): e for e in all_exercises}
        context['exercise_map'] = exercise_map
        context['workout_structure'] = workout_plan.workout_structure if isinstance(workout_plan.workout_structure, list) else []
        print('this is the map passed',context['workout_structure'])

        return context

class EditWorkoutPlanView(LoginRequiredMixin, TrainerRequiredMixin, SubscriptionRequiredMixin, TrainerOwnedMixin, UpdateView):
    model = WorkoutPlan
    form_class = WorkoutPlanForm
    template_name = 'workouts/edit.html'
    success_url = reverse_lazy('workouts:list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['trainer'] = get_object_or_404(TrainerProfile, user=self.request.user)
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, 'Workout plan updated successfully!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'There was an error saving your workout plan. Please check the fields.')
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # keep same days list as create view
        context['days'] = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        # Ensure the template sees 'plan_form' (alias for the UpdateView's form)
        # kwargs may contain 'plan_form' when re-rendering after invalid POST
        context['plan_form'] = kwargs.get('plan_form') or context.get('form') or self.get_form()

        # Provide sched_form: try to load an existing schedule for this plan, otherwise empty form
        schedule_instance = None
        try:
            schedule_instance = WorkoutSchedule.objects.filter(workout_plan=self.get_object()).first()
        except Exception:
            schedule_instance = None
        context['sched_form'] = kwargs.get('sched_form') or WorkoutScheduleForm(instance=schedule_instance)

        # Provide workout_structure (list) for templates that read it
        plan = self.get_object()
        if isinstance(plan.workout_structure, str):
            try:
                workout_data = json.loads(plan.workout_structure)
            except json.JSONDecodeError:
                workout_data = []
        else:
            workout_data = plan.workout_structure or []

        # Pass JSON string safely to template
        context['workout_json'] = json.dumps(workout_data)
        print(context['workout_json'], 'this is the json passed')
        return context

class DeleteWorkoutPlanView(LoginRequiredMixin, TrainerRequiredMixin, SubscriptionRequiredMixin, TrainerOwnedMixin, DeleteView):
    model = WorkoutPlan
    template_name = 'workouts/delete.html'
    success_url = reverse_lazy('workouts:list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Workout plan deleted successfully!')
        return super().delete(request, *args, **kwargs)

class ExerciseListView(LoginRequiredMixin, ListView):
    model = Exercise
    template_name = 'workouts/exercise_list.html'
    context_object_name = 'exercises'
    paginate_by = 30
    
    def get_queryset(self):
        queryset = Exercise.objects.filter(is_active=True)
        
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        equipment = self.request.GET.get('equipment')
        if equipment:
            queryset = queryset.filter(equipment_needed=equipment)
        
        return queryset.order_by('name')

class ExerciseDetailView(LoginRequiredMixin, DetailView):
    model = Exercise
    template_name = 'workouts/exercise_detail.html'
    context_object_name = 'exercise'
    
    
    
    def get_queryset(self):
        return Exercise.objects.filter(is_active=True)