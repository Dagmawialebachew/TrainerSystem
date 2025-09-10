from datetime import datetime, timedelta
from django.db import models
from django.conf import settings
from django.urls import reverse
from apps.clients.models import ClientProfile
from apps.trainers.models import TrainerProfile
from apps.workouts.models import WorkoutPlan

DAY_NAME_TO_IDX = {
  'Mon': 0, 'Tue': 1, 'Wed': 2,
  'Thu': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6
}


class WorkoutSchedule(models.Model):
    """Schedule for a client's weekly workout plan"""
    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE, related_name='workout_schedules')
    trainer = models.ForeignKey(TrainerProfile, on_delete=models.CASCADE, related_name='workout_schedules')
    workout_plan = models.ForeignKey(WorkoutPlan, on_delete=models.CASCADE, related_name='schedules')
    
    # Schedule settings
    weekly_sessions = models.PositiveIntegerField(default=3)
    trainer_approve_required = models.BooleanField(default=False)
    
    #New fields
    start_date= models.DateField(default=datetime.now)
    end_date= models.DateField(null=True, blank=True)
    default_start_time = models.TimeField(default="09:00")
    default_duration   = models.DurationField(default=timedelta(hours=1))
    # Optional notes
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.client.user.get_full_name()} Schedule ({self.workout_plan.title})"

    def get_absolute_url(self):
        return reverse('schedule:detail', kwargs={'pk': self.pk})
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            # auto–create first session on start_date
            from .models import WorkoutSession
            session_end = (
                datetime.combine(self.start_date, self.default_start_time)
                + self.default_duration
            ).time()
            WorkoutSession.objects.create(
                schedule=self,
                date=self.start_date,
                start_time=self.default_start_time,
                end_time=session_end
          )
            
    

    def generate_sessions(self):
        from .models import WorkoutSession
        print('generationg is runing')

        # 1) parse client preference
        raw = (self.client.preferred_workout_days or "")
        days = [d.strip() for d in raw.split(',') if d.strip()]
        weekday_idxs = {DAY_NAME_TO_IDX[d] for d in days if d in DAY_NAME_TO_IDX}

        # 2) clear old sessions
        self.sessions.all().delete()

        # 3) compute end
        end = self.end_date or (
            self.start_date + timedelta(weeks=4)
        )

        current = self.start_date
        while current <= end:
            # only schedule on preferred weekdays
            if current.weekday() in weekday_idxs:
                # enforce max per week
                week_start = current - timedelta(days=current.weekday())
                week_end   = week_start + timedelta(days=6)
                count = WorkoutSession.objects.filter(
                    schedule=self,
                    date__gte=week_start,
                    date__lte=week_end
                ).count()
                if count < self.weekly_sessions:
                    # build session times
                    start = self.default_start_time
                    end_t = (
                      datetime.combine(current, start)
                      + self.default_duration
                    ).time()

                    WorkoutSession.objects.create(
                      schedule=self,
                      date=current,
                      start_time=start,
                      end_time=end_t
                    )
            current += timedelta(days=1)


class WorkoutSession(models.Model):
    """A specific session within a workout schedule"""
    schedule = models.ForeignKey(WorkoutSchedule, on_delete=models.CASCADE, related_name='sessions')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    trainer_approved = models.BooleanField(default=False)
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"{self.schedule.client.user.get_full_name()} - {self.date} ({self.start_time}-{self.end_time})"


class TimeBlock(models.Model):
    """Time block for each session (allows finer granularity)"""
    session = models.ForeignKey(WorkoutSession, on_delete=models.CASCADE, related_name='time_blocks')
    start_time = models.TimeField()
    end_time = models.TimeField()
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['start_time']

    def __str__(self):
        return f"{self.session} Block ({self.start_time}-{self.end_time})"
