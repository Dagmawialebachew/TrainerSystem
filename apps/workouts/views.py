from datetime import datetime, timezone
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
from django.db.models import Q
from apps.core.mixins import TrainerRequiredMixin, SubscriptionRequiredMixin, TrainerOwnedMixin
from .models import WorkoutPlan, Exercise
from .forms import ExerciseForm, WorkoutPlanForm

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
            print('this is the plan bassed', plan)
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
from apps.workouts.utils import enrich_workout_structure

class WorkoutPlanDetailView(LoginRequiredMixin, TrainerOwnedMixin, DetailView):
    model = WorkoutPlan
    template_name = "workouts/detail_trainer.html"
    context_object_name = "workout_plan"
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(enrich_workout_structure(self.object))
        ctx.update({
            "is_trainer": True,
            "can_complete": False,
            "show_trainer_tools": True,
            "back_url": reverse_lazy("workouts:list"),
            "analytics": {
                "completed_this_week": 0,
                "adherence": 0,
                "streak": 0,
            }
        })
        return ctx


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
        return context

class DeleteWorkoutPlanView(LoginRequiredMixin, TrainerRequiredMixin, SubscriptionRequiredMixin, TrainerOwnedMixin, DeleteView):
    model = WorkoutPlan
    template_name = 'workouts/delete.html'
    success_url = reverse_lazy('workouts:list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Workout plan deleted successfully!')
        return super().delete(request, *args, **kwargs)

from django.db.models import Q

class TrainerExerciseListView(ListView):
    model = Exercise
    template_name = 'workouts/exercise_list.html'
    context_object_name = 'exercises'
    paginate_by = 12

    def get_queryset(self):
        trainer = self.request.user  # Assuming your user has a related TrainerProfile
        qs = Exercise.objects.filter(
            Q(is_global=True) | Q(trainer=trainer),
            is_active=True
        )

        query = self.request.GET.get("search", "").strip()
        if query:
            qs = qs.filter(
                Q(name__icontains=query) |
                Q(category__icontains=query) |
                Q(muscle_groups__icontains=query) |
                Q(equipment_needed__icontains=query)
            )
        return qs.order_by('name')



class TrainerExerciseCreateView(CreateView):
    model = Exercise
    form_class = ExerciseForm
    template_name = 'workouts/exercise_form.html'
    success_url = reverse_lazy('workouts:exercise_list')
    

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['trainer'] = self.request.user
        return kwargs

    def form_valid(self, form,):
        form.instance.trainer = self.request.user 
        messages.success(self.request, 'Exercise is created succefully')
        print('it is is valid')
        # ensure trainer is saved
        return super().form_valid(form)
    
    def form_invalid(self, form):
          # <-- this will show why it failed
        return super().form_invalid(form)



class TrainerExerciseUpdateView(UpdateView):
    model = Exercise
    form_class = ExerciseForm
    template_name = 'workouts/exercise_form.html'
    success_url = reverse_lazy('workouts:exercise_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['trainer'] = self.request.user
        return kwargs
    
    def form_valid(self, form,):
        form.instance.trainer = self.request.user 
        messages.success(self.request, 'Exercise is created succefully')        # ensure trainer is saved
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


class TrainerExerciseDeleteView(DeleteView):
    model = Exercise
    template_name = 'workouts/exercise_confirm_delete.html'
    success_url = reverse_lazy('workouts:exercise_list')
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Exercise is deleted successfully!')
        return super().delete(request, *args, **kwargs)