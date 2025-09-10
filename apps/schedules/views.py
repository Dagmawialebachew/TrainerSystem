from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from apps.core.mixins import TrainerRequiredMixin, SubscriptionRequiredMixin, TrainerOwnedMixin, ClientOwnedMixin, LoginRequiredMixin
from django.contrib import messages
from .models import WorkoutSchedule, TimeBlock, WorkoutSession
from .forms import WorkoutSessionForm

class ScheduleCalendarView(TrainerRequiredMixin, SubscriptionRequiredMixin, TemplateView):
    template_name = 'schedule/schedule_calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sessions'] = WorkoutSession.objects.filter(
            schedule__trainer=self.request.user.trainer_profile
        ).order_by('date', 'start_time')
        context["weekdays"] = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        context["days"] = range(1, 32)
        context["hours"] = range(0,24)
       

        return context

# -----------------------------------------
# WORKOUT SCHEDULE
# -----------------------------------------
class WorkoutScheduleListView(TrainerRequiredMixin, SubscriptionRequiredMixin, TrainerOwnedMixin, ListView):
    model = WorkoutSchedule
    template_name = 'schedule/schedule_list.html'
    context_object_name = 'schedules'


class WorkoutScheduleDetailView(TrainerRequiredMixin, SubscriptionRequiredMixin, TrainerOwnedMixin, DetailView):
    model = WorkoutSchedule
    template_name = 'schedule/schedule_detail.html'
    context_object_name = 'schedule'


class WorkoutScheduleCreateView(TrainerRequiredMixin, SubscriptionRequiredMixin, CreateView):
    model = WorkoutSchedule
    template_name = 'schedule/schedule_form.html'
    fields = ['client', 'workout_plan', 'weekly_sessions', 'trainer_approve_required', 'notes']

    def form_valid(self, form):
        # auto assign trainer from request
        form.instance.trainer = self.request.user.trainer_profile
        # if trainer created, auto-approve required is true
        form.instance.trainer_approve_required = True
        return super().form_valid(form)


class WorkoutScheduleUpdateView(TrainerRequiredMixin, SubscriptionRequiredMixin, TrainerOwnedMixin, UpdateView):
    model = WorkoutSchedule
    template_name = 'schedule/schedule_form.html'
    fields = ['client', 'workout_plan', 'weekly_sessions', 'trainer_approve_required', 'notes']


class WorkoutScheduleDeleteView(TrainerRequiredMixin, SubscriptionRequiredMixin, TrainerOwnedMixin, DeleteView):
    model = WorkoutSchedule
    template_name = 'schedule/schedule_confirm_delete.html'
    success_url = reverse_lazy('schedule:list')

# -----------------------------------------
# Workout Session
# -----------------------------------------


class WorkoutSessionListView(TrainerRequiredMixin, SubscriptionRequiredMixin, TrainerOwnedMixin, ListView):
    model = WorkoutSession
    template_name = 'schedule/session_list.html'
    context_object_name = 'sessions'
    


class WorkoutSessionDetailView(TrainerRequiredMixin, SubscriptionRequiredMixin, DetailView):
    model = WorkoutSession
    template_name = 'schedule/session_detail.html'
    context_object_name = 'session'

    def get_queryset(self):
        # Filter sessions where the related schedule belongs to the current trainer
        return WorkoutSession.objects.filter(
            schedule__trainer=self.request.user.trainer_profile
        )
class WorkoutSessionCreateView(TrainerRequiredMixin, SubscriptionRequiredMixin, TrainerOwnedMixin, CreateView):
    model = WorkoutSession
    template_name = 'schedule/session_form.html'
    fields = ['schedule', 'date', 'start_time', 'end_time', 'trainer_approved', 'notes']

    def form_valid(self, form):
        # auto-approve trainer sessions
        form.instance.trainer_approved = True
        return super().form_valid(form)


class WorkoutSessionUpdateView(LoginRequiredMixin, UpdateView):
    model = WorkoutSession
    template_name = 'schedule/session_form.html'
    form_class = WorkoutSessionForm

    def get_queryset(self):
        # Ensure only the owning trainer can edit
        return WorkoutSession.objects.filter(
            schedule__trainer=self.request.user.trainer_profile
        )

    def form_valid(self, form):
        messages.success(self.request, "Session updated successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('schedule:session_detail', kwargs={'pk': self.object.pk})

class WorkoutSessionDeleteView(TrainerRequiredMixin, SubscriptionRequiredMixin, TrainerOwnedMixin, DeleteView):
    model = WorkoutSession
    template_name = 'schedule/session_confirm_delete.html'
    success_url = reverse_lazy('schedule:session_list')

class WorkoutSessionApproveView(LoginRequiredMixin, View):
    """
    POST only. Approves the session if it belongs to current trainer.
    URL name: schedule:session_approve
    """
    def post(self, request, pk):
        session = get_object_or_404(
            WorkoutSession,
            pk=pk,
            schedule__trainer=request.user.trainer_profile
        )
        session.trainer_approved = True
        session.save(update_fields=['trainer_approved'])
        messages.success(request, "Session approved.")
        return redirect('schedule:session_detail', pk=pk)

    def get(self, request, pk):
        return HttpResponseBadRequest("Invalid method")


class WorkoutSessionRescheduleView(LoginRequiredMixin, View):
    """
    POST only. Updates date, start_time, end_time from modal form.
    URL name: schedule:session_reschedule
    """
    def post(self, request, pk):
        session = get_object_or_404(
            WorkoutSession,
            pk=pk,
            schedule__trainer=request.user.trainer_profile
        )

        date = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        if not (date and start_time and end_time):
            messages.error(request, "Please provide date, start time, and end time.")
            return redirect('schedule:session_detail', pk=pk)

        # Optional: validate that end_time > start_time
        try:
            from datetime import datetime
            st = datetime.strptime(start_time, "%H:%M")
            et = datetime.strptime(end_time, "%H:%M")
            if et <= st:
                messages.error(request, "End time must be after start time.")
                return redirect('schedule:session_detail', pk=pk)
        except ValueError:
            messages.error(request, "Invalid time format.")
            return redirect('schedule:session_detail', pk=pk)

        # Persist changes
        session.date = date
        session.start_time = start_time
        session.end_time = end_time
        session.trainer_approved = False  # auto-unapprove after change (optional but sensible)
        session.save(update_fields=['date', 'start_time', 'end_time', 'trainer_approved'])

        messages.success(request, "Session rescheduled. Approval reset to Pending.")
        return redirect('schedule:session_detail', pk=pk)

    def get(self, request, pk):
        return HttpResponseBadRequest("Invalid method")



#Time Block

class TimeBlockListView(TrainerRequiredMixin, SubscriptionRequiredMixin, TrainerOwnedMixin, ListView):
    model = TimeBlock
    template_name = 'schedule/timeblock_list.html'
    context_object_name = 'timeblocks'


class TimeBlockCreateView(TrainerRequiredMixin, SubscriptionRequiredMixin, TrainerOwnedMixin, CreateView):
    model = TimeBlock
    template_name = 'schedule/timeblock_form.html'
    fields = ['session', 'start_time', 'end_time', 'notes']


class TimeBlockUpdateView(TrainerRequiredMixin, SubscriptionRequiredMixin, TrainerOwnedMixin, UpdateView):
    model = TimeBlock
    template_name = 'schedule/timeblock_form.html'
    fields = ['session', 'start_time', 'end_time', 'notes']


class TimeBlockDeleteView(TrainerRequiredMixin, SubscriptionRequiredMixin, TrainerOwnedMixin, DeleteView):
    model = TimeBlock
    template_name = 'schedule/timeblock_confirm_delete.html'
    success_url = reverse_lazy('schedule:timeblock_list')
