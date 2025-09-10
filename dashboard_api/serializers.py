# apps/schedule/serializers.py
from rest_framework import serializers
from apps.schedules.models import WorkoutSchedule, WorkoutSession, TimeBlock


class WorkoutScheduleSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source="client.user.get_full_name", read_only=True)
    workout_plan_title = serializers.CharField(source="workout_plan.title", read_only=True)

    class Meta:
        model = WorkoutSchedule
        fields = [
            "id",
            "client",
            "client_name",
            "workout_plan",
            "workout_plan_title",
            "weekly_sessions",
            "trainer_approve_required",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class WorkoutSessionSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source="schedule.client.user.get_full_name", read_only=True)
    workout_plan_title = serializers.CharField(source="schedule.workout_plan.title", read_only=True)
    color = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = WorkoutSession
        fields = [
            "id",
            "schedule",
            "date",
            "start_time",
            "end_time",
            "trainer_approved",
            "notes",
            "client_name",
            "workout_plan_title",
            "color",
            "status",
        ]

    def get_color(self, obj):
        if obj.trainer_approved:
            return "bg-green-500"
        return "bg-yellow-500"

    def get_status(self, obj):
        if obj.trainer_approved:
            return "Approved"
        return "Pending"


class TimeBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeBlock
        fields = [
            "id",
            "session",
            "start_time",
            "end_time",
            "notes",
        ]
