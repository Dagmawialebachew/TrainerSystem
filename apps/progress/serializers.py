# progress/serializers.py
from rest_framework import serializers
from .models import ClientProgress

class ClientProgressSummarySerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.user.get_full_name')

    class Meta:
        model = ClientProgress
        fields = [
            'client_name', 'date',
            'workout_completed', 'meal_plan_followed',
            'energy_level', 'sleep_hours', 'stress_level'
        ]
