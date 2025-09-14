from datetime import date, datetime, time, timedelta
import json
from django.http import JsonResponse
from httpx import Response
from rest_framework import viewsets, permissions
from apps.clients.models import ClientProfile
from apps.schedules.models import WorkoutSchedule, WorkoutSession, TimeBlock
from .serializers import WorkoutScheduleSerializer, WorkoutSessionSerializer, TimeBlockSerializer
from apps.core.mixins import TrainerRequiredMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from apps.progress.models import ClientProgress  # 👈 Import your model
from apps.workouts.models import Exercise
from django.views.decorators.http import require_GET
from django.db.models import Q

class WorkoutScheduleViewSet(viewsets.ModelViewSet):
    queryset = WorkoutSchedule.objects.all()
    serializer_class = WorkoutScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'trainer_profile'):
            return self.queryset.filter(trainer=user.trainer_profile)
        return self.queryset.none()


class WorkoutSessionViewSet(viewsets.ModelViewSet):
    queryset = WorkoutSession.objects.all()
    serializer_class = WorkoutSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'trainer_profile'):
            return self.queryset.filter(schedule__trainer=user.trainer_profile)
        elif hasattr(user, 'client_profile'):
            return self.queryset.filter(schedule__client=user.client_profile)
        return self.queryset.none()

MOTIVATIONAL_QUOTES = [
    "Push yourself, because no one else is going to do it for you.",
    "Success starts with self-discipline.",
    "Every workout counts, no matter how small.",
    "Stronger every day, one rep at a time.",
    "Stay consistent, results will follow."
]

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

@method_decorator(csrf_exempt, name="dispatch")

class EngagementSummaryView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_streak(self, client_profile):
        """Calculate streak based on consecutive daily ClientProgress logs."""
        today = date.today()
        progresses = (
            ClientProgress.objects.filter(client=client_profile)
            .order_by("-created_at")
            .values_list("created_at", flat=True)
        )

        if not progresses:
            return 0

        streak = 0
        current_day = today

        for created_at in progresses:
            log_day = created_at.date()
            if log_day == current_day:
                streak += 1
                current_day -= timedelta(days=1)
            elif log_day == current_day - timedelta(days=1):
                streak += 1
                current_day -= timedelta(days=1)
            else:
                break
        return streak

    def get(self, request):
        user = request.user

        # 1. Streak counter
        streak = 0
        if hasattr(user, "client_profile"):
            streak = self.get_streak(user.client_profile)

        # 2. Daily motivational quote
        today = date.today()
        quote = MOTIVATIONAL_QUOTES[today.day % len(MOTIVATIONAL_QUOTES)]

        # 3. Today's sessions with timeblocks
        today_sessions = []
        if hasattr(user, "client_profile"):
            sessions = (
                WorkoutSession.objects.filter(
                    schedule__client=user.client_profile,
                    date=today
                )
                .prefetch_related("time_blocks")
                .order_by("start_time")
            )

            now = datetime.now().time()

            for session in sessions:
                blocks = []

                # Include actual time blocks if any
                if session.time_blocks.exists():
                    for block in session.time_blocks.all().order_by("start_time"):
                        status = "completed" if block.end_time < now else "pending"
                        blocks.append({
                            "start_time": block.start_time.strftime("%H:%M"),
                            "end_time": block.end_time.strftime("%H:%M"),
                            "status": status,
                        })
                else:
                    # Fallback: use session start/end as a single block
                    status = "completed" if session.end_time < now else "pending"
                    blocks.append({
                        "start_time": session.start_time.strftime("%H:%M"),
                        "end_time": session.end_time.strftime("%H:%M"),
                        "status": status,
                    })

                today_sessions.append({
                    "title": session.schedule.workout_plan.title,
                    "session_start": session.start_time.strftime("%H:%M"),
                    "session_end": session.end_time.strftime("%H:%M"),
                    "timeblocks": blocks,
                })

        # 4. Next upcoming session
        next_event = None
        if hasattr(user, "client_profile"):
            next_session = (
                WorkoutSession.objects.filter(
                    schedule__client=user.client_profile,
                    date__gte=today,
                )
                .order_by("date", "start_time")
                .first()
            )

            if next_session:
                blocks = []
                now = datetime.now().time()

                if next_session.time_blocks.exists():
                    for block in next_session.time_blocks.all().order_by("start_time"):
                        status = "completed" if block.end_time < now else "pending"
                        blocks.append({
                            "start_time": block.start_time.strftime("%H:%M"),
                            "end_time": block.end_time.strftime("%H:%M"),
                            "status": status,
                        })
                else:
                    status = "completed" if next_session.end_time < now else "pending"
                    blocks.append({
                        "start_time": next_session.start_time.strftime("%H:%M"),
                        "end_time": next_session.end_time.strftime("%H:%M"),
                        "status": status,
                    })

                next_event = {
                    "title": next_session.schedule.workout_plan.title,
                    "session_start": next_session.start_time.strftime("%H:%M"),
                    "session_end": next_session.end_time.strftime("%H:%M"),
                    "timeblocks": blocks,
                }

        return Response({
            "streak": streak,
            "quote": quote,
            "today_sessions": today_sessions,
            "next_event": next_event,
        })
        

         
class TimeBlockViewSet(viewsets.ModelViewSet):
    queryset = TimeBlock.objects.all()
    serializer_class = TimeBlockSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'trainer_profile'):
            return self.queryset.filter(session__schedule__trainer=user.trainer_profile)
        elif hasattr(user, 'client_profile'):
            return self.queryset.filter(session__schedule__client=user.client_profile)
        return self.queryset.none()

#Get client days
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

VALID = {"Mon","Tue","Wed","Thu","Fri","Sat","Sun"}
@method_decorator(csrf_exempt, name="dispatch")

class ClientDaysView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, client_id):
        try:
            client = ClientProfile.objects.get(pk=client_id)
            raw = client.preferred_workout_days or ""
            days = [d.strip() for d in raw.split(",") if d.strip()]
            normalized = [d for d in days if d in VALID]
            return Response({"days": normalized}, status=status.HTTP_200_OK)
        except ClientProfile.DoesNotExist:
            return Response({"days": []}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, client_id):
        try:
            client = ClientProfile.objects.get(pk=client_id)
        except ClientProfile.DoesNotExist:
            return Response({"detail": "Client not found"}, status=status.HTTP_404_NOT_FOUND)

        days = request.data.get("days", [])
        if not isinstance(days, list):
            return Response({"detail": "Invalid format"}, status=status.HTTP_400_BAD_REQUEST)

        normalized = [d for d in days if d in VALID]
        if not normalized:
            return Response({"detail": "No valid days provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Persist as "Mon, Wed, Fri"
        client.preferred_workout_days = ", ".join(normalized)
        client.save(update_fields=["preferred_workout_days"])

        return Response({"days": normalized}, status=status.HTTP_200_OK)
    
    
    
    

# workouts/views_api.py
from django.views import View
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from apps.workouts.models import WorkoutPlan, ExerciseProgress
from apps.workouts.utils import compute_streak, summarize_day_progress

@method_decorator(login_required, name='dispatch')
class WorkoutCompleteView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body or "{}")
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON")

        client_id = data.get("client_id")
        plan_id = data.get("plan_id")
        day = data.get("day")
        exercise_name = data.get("exercise_name")
        if not all([client_id, plan_id, day, exercise_name]):
            return HttpResponseBadRequest("Missing fields")

        plan = get_object_or_404(WorkoutPlan, id=plan_id, client_id=client_id)
        ExerciseProgress.objects.get_or_create(
            client_id=client_id,
            workout_plan=plan,
            day=day,
            exercise_name=exercise_name,
            defaults={"completed_at": datetime.now()}
        )

        prog_qs = ExerciseProgress.objects.filter(client_id=client_id, workout_plan=plan)
        streak = compute_streak(prog_qs)
        today_name = datetime.now().strftime("%A")
        summary = summarize_day_progress(plan.workout_structure if isinstance(plan.workout_structure, list) else [],
                                         prog_qs, today_name)

        return JsonResponse({
            "ok": True,
            "streak": streak,
            "today": {
                "day": today_name,
                "completed": summary["completed"],
                "total": summary["total"]
            }
        })


@method_decorator(login_required, name='dispatch')
class TodayWorkoutView(View):
    def get(self, request, *args, **kwargs):
        client_id = request.GET.get('client_id')
        plan_id = request.GET.get('plan_id')
        if not all([client_id, plan_id]):
            return HttpResponseBadRequest("Missing client_id or plan_id")

        plan = get_object_or_404(WorkoutPlan, id=plan_id, client_id=client_id)
        today_name = datetime.now().strftime("%A")
        prog_qs = ExerciseProgress.objects.filter(client_id=client_id, workout_plan=plan)
        day_summary = summarize_day_progress(plan.workout_structure if isinstance(plan.workout_structure, list) else [],
                                             prog_qs, today_name)

        return JsonResponse({
            "day": today_name,
            "exercises": day_summary["exercises"],
            "completed": day_summary["completed"],
            "total": day_summary["total"]
        })


@method_decorator(login_required, name='dispatch')
class MotivationView(View):
    COPY = {
        "beginner": [
            "Small steps, big change. Keep moving.",
            "Form first. Progress follows."
        ],
        "intermediate": [
            "Consistency beats intensity.",
            "Stack wins. Build momentum."
        ],
        "advanced": [
            "Discipline is the flex.",
            "Pressure creates diamonds."
        ],
        "default": ["Show up. That’s the secret."]
    }
    def get(self, request, *args, **kwargs):
        level = (request.GET.get('level') or 'default').lower()
        msgs = self.COPY.get(level, self.COPY['default'])
        ts = int(datetime.now().timestamp())
        return JsonResponse({"message": msgs[ts % len(msgs)]})


@method_decorator(login_required, name='dispatch')
class WorkoutAnalyticsView(View):
    def get(self, request, *args, **kwargs):
        client_id = request.GET.get("client_id")
        plan_id = request.GET.get("plan_id")
        if not client_id or not plan_id:
            return HttpResponseBadRequest("Missing client_id or plan_id")

        plan = get_object_or_404(WorkoutPlan, id=plan_id, client_id=client_id)
        structure = plan.workout_structure if isinstance(plan.workout_structure, list) else []

        progress_qs = ExerciseProgress.objects.filter(client_id=client_id, workout_plan=plan)

        # Completed this week
        today = datetime.today()
        start_of_week = today - timedelta(days=today.weekday())
        completed_this_week = progress_qs.filter(completed_at__date__gte=start_of_week.date()).count()

        # Total planned
        total_planned = sum(len(day.get("exercises", [])) for day in structure)
        total_completed = progress_qs.count()
        adherence = round((total_completed / total_planned) * 100, 1) if total_planned else 0

        # Streak
        days = set(progress_qs.values_list("completed_at__date", flat=True))
        streak = 0
        d = today.date()
        while d in days:
            streak += 1
            d -= timedelta(days=1)

        # Notes
        notes = plan.ai_suggestions if plan.ai_enhanced else ""

        return JsonResponse({
            "completed_this_week": completed_this_week,
            "adherence": adherence,
            "streak": streak,
            "notes": notes
        })
        
        

@method_decorator([require_GET, login_required], name='dispatch')
class ExerciseSearchView(View):
    def get(self, request, *args, **kwargs):
        q = request.GET.get("q", "").strip()
        try:
            limit = min(int(request.GET.get("limit", 10)), 25)
        except ValueError:
            return HttpResponseBadRequest("Invalid limit")

        if q:
            queryset = Exercise.objects.filter(
                Q(name__icontains=q) |
                Q(muscle_groups__icontains=q) |
                Q(category__icontains=q),
                is_active=True
            ).order_by("name")[:limit]
        else:
            queryset = Exercise.objects.filter(is_active=True).order_by("name")[:limit]

        results = [{
            "id": ex.pk,
            "name": ex.name,
            "category": ex.get_category_display(),
            "equipment": ex.get_equipment_needed_display(),
            "muscle_groups": ex.muscle_groups,
            "demo": ex.demonstration_video_url or "",
            "difficulty": ex.difficulty_level,
        } for ex in queryset]

        return JsonResponse({"results": results})