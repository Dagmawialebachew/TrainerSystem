# dump_kidus_data.py
import json
from django.core.serializers import serialize
from apps.accounts.models import User
from apps.clients.models import ClientsProfile
from apps.workouts.models import WorkoutPlan
from apps.progress.models import ProgressGoal, ClientProgress
from apps.schedules.models import WorkoutSchedule, WorkoutSession
from apps.nutrition.models import MealPlan, TrainerFood

kidus = User.objects.get(username='kidus')
client_profiles = ClientsProfile.objects.filter(user=kidus)
plans = WorkoutPlan.objects.filter(client__in=client_profiles)
goals = ProgressGoal.objects.filter(client__in=client_profiles)
progress = ClientProgress.objects.filter(client__in=client_profiles)
schedules = WorkoutSchedule.objects.filter(client__in=client_profiles)
sessions = WorkoutSession.objects.filter(client__in=client_profiles)
meal_plans = MealPlan.objects.filter(client__in=client_profiles)
trainer_foods = TrainerFood.objects.filter(trainer=kidus.trainerprofile)

data = (
    list(json.loads(serialize('json', [kidus]))) +
    list(json.loads(serialize('json', client_profiles))) +
    list(json.loads(serialize('json', plans))) +
    list(json.loads(serialize('json', goals))) +
    list(json.loads(serialize('json', progress))) +
    list(json.loads(serialize('json', schedules))) +
    list(json.loads(serialize('json', sessions))) +
    list(json.loads(serialize('json', meal_plans))) +
    list(json.loads(serialize('json', trainer_foods)))
)

with open('kidus_full_dump.json', 'w') as f:
    json.dump(data, f, indent=2)
