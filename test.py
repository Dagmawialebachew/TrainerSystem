from django.utils import timezone
from django.contrib.auth.hashers import make_password
from apps.accounts.models import User
from apps.trainers.models import TrainerProfile
from apps.clients.models import ClientProfile

# ─── Trainer User ─────────────────────────────────────────────────────────────
trainer_user = User.objects.create(
    username="trainerlayke",
    first_name="Layke",
    last_name="Mariam",
    email="layke.mariam@gmail.com",
    role="trainer",
    phone_number="0911001100",
    date_of_birth="1989-04-12",
    is_active=True,
    is_staff=True,
    is_active_subscription=True,
    password=make_password("fitnessdemo8"),
    created_at=timezone.now(),
    updated_at=timezone.now()
)

trainer_profile = TrainerProfile.objects.create(
    user=trainer_user,
    business_name="Layke Mariam Fitness",
    bio="Ethiopian coach blending flexibility, strength, and fasting-aware programs.",
    specializations="flexibility",
    experience_years=8,
    certifications="ACE CPT; Ethiopian Sports Council Accreditation",
    is_paid=True,
    package="basic",
    brand_color="#3B82F6",
    address="Bole, Addis Ababa, Ethiopia",
    city="Addis Ababa",
    website="https://fithabesha.et",
    instagram="fithabesha",
    hourly_rate=450.00,
    is_accepting_clients=True,
    is_verified=True
)

# ─── Ethiopian Client Profiles ────────────────────────────────────────────────
ethiopian_clients = [
    {"username": "liyae@12", "name": "Liya Fikremariam", "goal": "weight_loss", "level": "beginner", "height": 162, "weight": 76, "target": 64, "days": "Mon, Wed, Fri"},
    {"username": "nahi@12", "name": "Nahom Worku", "goal": "muscle_gain", "level": "intermediate", "height": 181, "weight": 73, "target": 82, "days": "Tue, Thu, Sat"},
    {"username": "rediet@12", "name": "Rediet Hailu", "goal": "flexibility", "level": "beginner", "height": 158, "weight": 55, "target": 53, "days": "Mon, Thu"},
    {"username": "biruk@12", "name": "Biruk Tsegaye", "goal": "general_fitness", "level": "intermediate", "height": 174, "weight": 69, "target": 67, "days": "Wed, Fri, Sun"},
    {"username": "marth@18", "name": "Martha Kebede", "goal": "strength", "level": "advanced", "height": 170, "weight": 64, "target": 68, "days": "Mon, Tue, Thu, Sat"},
]



for i, client in enumerate(ethiopian_clients, start=1):
    first, last = client["name"].split()
    user = User.objects.create(
        username=client["username"],
        first_name=first,
        last_name=last,
        email=f"{client['username']}@example.com",
        role="client",
        phone_number=f"09120011{i:02}",
        date_of_birth="1990-01-01",
        is_active=True,
        password=make_password("fitnessdemo8"),
        created_at=timezone.now(),
        updated_at=timezone.now()
    )

    ClientProfile.objects.create(
        user=user,
        trainer=trainer_profile,
        fitness_goal=client["goal"],
        fitness_level=client["level"],
        height=client["height"],
        current_weight=client["weight"],
        target_weight=client["target"],
        dietary_restrictions="none",
        medical_conditions="",
        allergies="",
        preferred_workout_days=client["days"],
        workout_duration_preference=60,
        weekly_sessions=3,
        notes="Demo client for Leyke",
        is_active=True,
        start_date=timezone.now().date(),
        created_at=timezone.now(),
        updated_at=timezone.now()
    )

print("✅ Demo trainer and 6 Ethiopian clients created successfully.")





from django.utils import timezone
from apps.accounts.models import User
from apps.trainers.models import TrainerProfile
from apps.clients.models import ClientProfile
from apps.workouts.models import WorkoutPlan

# Sample workout structure
# structure = [
#     {"day": "Monday", "exercises": [
#         {"name": "Plank", "sets": 4, "reps": 18},
#         {"name": "Crunches", "sets": 3, "reps": 12},
#         {"name": "Mountain Climbers", "sets": 5, "reps": 17},
#         {"name": "Lunges", "sets": 4, "reps": 11},
#         {"name": "Lunges", "sets": 4, "reps": 18}
#     ]},
#     {"day": "Tuesday", "exercises": [
#         {"name": "Mountain Climbers", "sets": 5, "reps": 18},
#         {"name": "Crunches", "sets": 4, "reps": 14},
#         {"name": "Lunges", "sets": 5, "reps": 12},
#         {"name": "Lunges", "sets": 4, "reps": 17},
#         {"name": "Bicep Curls", "sets": 3, "reps": 13}
#     ]},
#     {"day": "Wednesday", "exercises": [
#         {"name": "Plank", "sets": 4, "reps": 17},
#         {"name": "Dumbbell Shoulder Press", "sets": 5, "reps": 11},
#         {"name": "Plank", "sets": 3, "reps": 15},
#         {"name": "Squats", "sets": 4, "reps": 15},
#         {"name": "Mountain Climbers", "sets": 5, "reps": 16}
#     ]},
#     {"day": "Thursday", "exercises": [
#         {"name": "Lunges", "sets": 4, "reps": 16},
#         {"name": "Bicep Curls", "sets": 3, "reps": 15},
#         {"name": "Bicep Curls", "sets": 5, "reps": 10},
#         {"name": "Tricep Dips", "sets": 3, "reps": 19}
#     ]},
#     {"day": "Friday", "exercises": [
#         {"name": "Crunches", "sets": 3, "reps": 14},
#         {"name": "Squats", "sets": 5, "reps": 13},
#         {"name": "Push-ups", "sets": 4, "reps": 14},
#         {"name": "Mountain Climbers", "sets": 3, "reps": 12},
#         {"name": "Push-ups", "sets": 5, "reps": 18}
#     ]}
# ]

# Get trainer and clients
from random import sample, randint
from django.contrib.auth import get_user_model
from apps.clients.models import ClientProfile
from apps.workouts.models import WorkoutPlan
from apps.workouts.models import Exercise

trainer_user = User.objects.get(username="trainerlayke")
trainer_profile = trainer_user.trainer_profile
clients = ClientProfile.objects.filter(trainer=trainer_profile)# sample 2 clients

# Function to generate sets/reps based on difficulty
def get_sets_reps(exercise):
    level = exercise.difficulty_level
    if level == "beginner":
        return randint(2,3), randint(10,15)
    elif level == "intermediate":
        return randint(3,4), randint(12,20)
    else:  # advanced
        return randint(4,5), randint(15,25)

# Weekday options
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

for client in clients:
    # Choose exercises based on client's fitness level
    exercises_qs = Exercise.objects.filter(
        difficulty_level__in=[client.fitness_level.lower(), "beginner"]
    ).order_by("?")[:12]  # select 12 random exercises

    # Determine number of workout days for the client
    num_days = min(client.weekly_sessions, len(exercises_qs))
    
    # Pick random unique days
    selected_days = sample(WEEKDAYS, num_days)

    # Divide exercises across selected days
    chunk_size = len(exercises_qs) // num_days
    workout_structure = []
    for i, day in enumerate(selected_days):
        day_exercises = exercises_qs[i*chunk_size:(i+1)*chunk_size]
        exercises_list = []
        for ex in day_exercises:
            sets, reps = get_sets_reps(ex)
            exercises_list.append({
                "name": ex.name,
                "sets": sets,
                "reps": reps
            })
        workout_structure.append({
            "day": day,
            "exercises": exercises_list
        })

    # Build a dynamic title
    title = f"{client.fitness_level.title()} Plan"

    # Create workout plan
    plan, created = WorkoutPlan.objects.get_or_create(
        trainer = trainer_profile,
        client=client,
        title=title,
        difficulty=client.fitness_level,
        workout_structure=workout_structure,
        is_active=True,
        ai_enhanced=True,
        ai_suggestions="Auto-generated based on exercise database and client fitness level."
    )

    print(f"✅ Plan created for {client.user.get_full_name()}: {title}")



from django.utils import timezone
from apps.accounts.models import User
from apps.trainers.models import TrainerProfile
from apps.clients.models import ClientProfile
from apps.nutrition.models import MealPlan  # adjust if your app name is different

# Sample meal structure
structure = {
    "Monday": {
        "Breakfast": [{"name": "Chicken", "qty": "100"}],
        "Lunch": [],
        "Dinner": [],
        "Snacks": []
    },
    "Tuesday": {"Breakfast": [], "Lunch": [], "Dinner": [], "Snacks": []},
    "Wednesday": {"Breakfast": [], "Lunch": [], "Dinner": [], "Snacks": []},
    "Thursday": {"Breakfast": [], "Lunch": [], "Dinner": [], "Snacks": []},
    "Friday": {"Breakfast": [], "Lunch": [], "Dinner": [], "Snacks": []},
    "Saturday": {"Breakfast": [], "Lunch": [], "Dinner": [], "Snacks": []},
    "Sunday": {"Breakfast": [], "Lunch": [], "Dinner": [], "Snacks": []}
}

# Goal → Meal type mapping
goal_to_meal_type = {
    "weight_loss": "weight_loss",
    "muscle_gain": "muscle_gain",
    "strength": "performance",
    "endurance": "performance",
    "flexibility": "maintenance",
    "general_fitness": "maintenance",
    "rehabilitation": "therapeutic",
    "sports_performance": "performance"
}

# Goal → Title theme
goal_to_title = {
    "weight_loss": "Fasting Flex Plan",
    "muscle_gain": "Bulking Boost",
    "strength": "Power Meal Matrix",
    "endurance": "Enduro Fuel",
    "flexibility": "Mobility Meals",
    "general_fitness": "Balanced Habesha Plate",
    "rehabilitation": "Recovery Nourishment",
    "sports_performance": "Athlete's Edge Plan"
}

# Get trainer and clients
trainer_user = User.objects.get(username="trainerlayke")
trainer_profile = trainer_user.trainer_profile
clients = ClientProfile.objects.filter(trainer=trainer_profile)

# Create meal plans
for client in clients:
    goal = client.fitness_goal
    meal_type = goal_to_meal_type.get(goal, "maintenance")
    title = goal_to_title.get(goal, "Habesha Wellness Plan")
    full_name = client.user.get_full_name()

    MealPlan.objects.create(
        trainer=trainer_profile,
        client=client,
        title=title,
        description=f"Meal plan for {full_name} focused on {goal.replace('_', ' ').title()} goals.",
        meal_type=meal_type,
        daily_calories=2200,
        protein_grams=120,
        carbs_grams=250,
        fat_grams=70,
        meal_structure=structure,
        includes_traditional_foods=True,
        fasting_considerations="Includes fasting-compatible options for Wednesdays and Fridays.",
        is_active=True,
        start_date=timezone.now().date(),
        ai_enhanced=True,
        ai_suggestions="Generated using AI based on client goal, dietary preferences, and fasting days.",
        created_at=timezone.now(),
        updated_at=timezone.now()
    )

print("✅ Meal plans created for all clients under trainerlayke.")


from django.utils import timezone
from apps.trainers.models import TrainerProfile
from apps.nutrition.models import TrainerFood

trainer = TrainerProfile.objects.get(user__username="trainerlayke")

foods = [
    # Grains & Cereals
    {
        "name": "Injera",
        "category": "grains",
        "calories_per_100g": 126,
        "protein_per_100g": 4.0,
        "carbs_per_100g": 25.0,
        "fat_per_100g": 0.5,
        "fiber_per_100g": 3.0,
        "description": "Teff-based fermented flatbread, staple in Ethiopian meals.",
        "seasonal_availability": "Year-round",
        "cultural_significance": "Central to Ethiopian cuisine and communal eating.",
        "preparation_notes": "Fermented teff batter cooked on mitad.",
        "is_vegetarian": True,
        "is_vegan": True,
        "is_gluten_free": True,
        "is_fasting_friendly": True
    },
    {
        "name": "Kinche",
        "category": "grains",
        "calories_per_100g": 150,
        "protein_per_100g": 5.0,
        "carbs_per_100g": 28.0,
        "fat_per_100g": 2.0,
        "fiber_per_100g": 3.0,
        "description": "Cracked barley or oats boiled with spices.",
        "seasonal_availability": "Year-round",
        "cultural_significance": "Common breakfast dish.",
        "preparation_notes": "Boiled with water, salt, sometimes oil or flax.",
        "is_vegetarian": True,
        "is_vegan": True,
        "is_gluten_free": False,
        "is_fasting_friendly": True
    },

    # Legumes
    {
        "name": "Shiro Wot",
        "category": "legumes",
        "calories_per_100g": 180,
        "protein_per_100g": 8.0,
        "carbs_per_100g": 20.0,
        "fat_per_100g": 6.0,
        "fiber_per_100g": 5.0,
        "description": "Chickpea flour stew with spices.",
        "seasonal_availability": "Year-round",
        "cultural_significance": "Fasting staple, high in protein.",
        "preparation_notes": "Simmered with onions, garlic, berbere.",
        "is_vegetarian": True,
        "is_vegan": True,
        "is_gluten_free": True,
        "is_fasting_friendly": True
    },
    {
        "name": "Misir Wot",
        "category": "legumes",
        "calories_per_100g": 163,
        "protein_per_100g": 9.0,
        "carbs_per_100g": 20.0,
        "fat_per_100g": 5.0,
        "fiber_per_100g": 6.0,
        "description": "Red lentil stew with berbere spice.",
        "seasonal_availability": "Year-round",
        "cultural_significance": "Fasting-friendly and protein-rich.",
        "preparation_notes": "Cooked with onions, garlic, and oil.",
        "is_vegetarian": True,
        "is_vegan": True,
        "is_gluten_free": True,
        "is_fasting_friendly": True
    },

    # Vegetables
    {
        "name": "Gomen",
        "category": "vegetables",
        "calories_per_100g": 50,
        "protein_per_100g": 3.0,
        "carbs_per_100g": 7.0,
        "fat_per_100g": 1.0,
        "fiber_per_100g": 4.0,
        "description": "Stewed collard greens with garlic and oil.",
        "seasonal_availability": "Rainy season peak",
        "cultural_significance": "Served with injera, especially on fasting days.",
        "preparation_notes": "Sautéed with onions, garlic, and oil.",
        "is_vegetarian": True,
        "is_vegan": True,
        "is_gluten_free": True,
        "is_fasting_friendly": True
    },
    {
        "name": "Atkilt",
        "category": "vegetables",
        "calories_per_100g": 60,
        "protein_per_100g": 2.0,
        "carbs_per_100g": 12.0,
        "fat_per_100g": 1.0,
        "fiber_per_100g": 3.0,
        "description": "Cabbage, carrot, and potato mix.",
        "seasonal_availability": "Year-round",
        "cultural_significance": "Common side dish, especially during fasting.",
        "preparation_notes": "Steamed or sautéed with turmeric and garlic.",
        "is_vegetarian": True,
        "is_vegan": True,
        "is_gluten_free": True,
        "is_fasting_friendly": True
    },

    # Protein (non-fasting)
    {
        "name": "Doro Wot",
        "category": "meat",
        "calories_per_100g": 164,
        "protein_per_100g": 20.0,
        "carbs_per_100g": 5.0,
        "fat_per_100g": 8.0,
        "fiber_per_100g": 1.0,
        "description": "Spicy chicken stew with berbere and boiled eggs.",
        "seasonal_availability": "Holiday dish",
        "cultural_significance": "Served on holidays and special occasions.",
        "preparation_notes": "Slow-cooked with onions, garlic, berbere.",
        "is_vegetarian": False,
        "is_vegan": False,
        "is_gluten_free": True,
        "is_fasting_friendly": False
    },
    {
        "name": "Tibs",
        "category": "meat",
        "calories_per_100g": 154,
        "protein_per_100g": 22.0,
        "carbs_per_100g": 2.0,
        "fat_per_100g": 7.0,
        "fiber_per_100g": 0.5,
        "description": "Pan-fried beef or lamb cubes with spices.",
        "seasonal_availability": "Year-round",
        "cultural_significance": "Popular in restaurants and home meals.",
        "preparation_notes": "Cooked with onions, garlic, rosemary.",
        "is_vegetarian": False,
        "is_vegan": False,
        "is_gluten_free": True,
        "is_fasting_friendly": False
    },

    # Beverages
    {
        "name": "Telba",
        "category": "beverages",
        "calories_per_100g": 80,
        "protein_per_100g": 3.0,
        "carbs_per_100g": 5.0,
        "fat_per_100g": 6.0,
        "fiber_per_100g": 2.0,
        "description": "Flaxseed drink, often consumed during fasting.",
        "seasonal_availability": "Year-round",
        "cultural_significance": "Traditional fasting beverage.",
        "preparation_notes": "Ground flax mixed with water and spices.",
        "is_vegetarian": True,
        "is_vegan": True,
        "is_gluten_free": True,
        "is_fasting_friendly": True
    }
]

for f in foods:
    TrainerFood.objects.get_or_create(trainer=trainer, name=f["name"], defaults={**f, "created_at": timezone.now()})

print("✅ Ethiopian TrainerFood entries seeded for trainerlayke.")



from datetime import datetime, timedelta, time
from decimal import Decimal
from django.utils import timezone

from apps.accounts.models import User
from apps.trainers.models import TrainerProfile
from apps.clients.models import ClientProfile
from apps.workouts.models import WorkoutPlan
from apps.schedules.models import WorkoutSchedule, WorkoutSession
from apps.progress.models import ProgressGoal
from apps.payments.models import Payment, Subscription

now = timezone.now()
today = now.date()

trainer_user = User.objects.get(username="trainerlayke")
trainer = trainer_user.trainer_profile
clients = ClientProfile.objects.filter(trainer=trainer)

# ── Subscription ──
Subscription.objects.update_or_create(
    trainer=trainer,
    defaults={
        "package": "pro",
        "status": "active",
        "monthly_amount": Decimal("79.00"),
        "currency": "USD",
        "start_date": now - timedelta(days=60),
        "current_period_start": now - timedelta(days=15),
        "current_period_end": now + timedelta(days=15),
        "trial_end": None,
        "cancelled_at": None,
    }
)

# ── Per-client data ──
for client in clients:
    # WorkoutPlan fallback
    plan = client.workout_plans.first()
   

    # WorkoutSchedule
    # schedule, created = WorkoutSchedule.objects.get_or_create(
    #     client=client,
    #     trainer=trainer,
    #     workout_plan=plan,
    #     defaults={
    #         "weekly_sessions": client.weekly_sessions or 3,
    #         "trainer_approve_required": False,
    #         "start_date": today,
    #         "end_date": today + timedelta(weeks=4),
    #         "default_start_time": time(9, 0),
    #         "default_duration": timedelta(hours=1),
    #         "notes": "Generated from client preferences."
    #     }
    # )
    # if not created:
    #     schedule.start_date = today
    #     schedule.end_date = today + timedelta(weeks=4)
    #     schedule.default_start_time = time(9, 0)
    #     schedule.save()

    # schedule.generate_sessions()

    # # Approve first 2 sessions
    # for session in schedule.sessions.filter(date__gte=today).order_by("date")[:2]:
    #     session.trainer_approved = True
    #     session.notes = "Approved for demo."
    #     session.save()

    # ProgressGoal
    ProgressGoal.objects.update_or_create(
        client=client,
        trainer=trainer,
        title=f"{client.fitness_goal.replace('_',' ').title()} Goal",
        defaults={
            "description": "Demo goal based on fitness objective.",
            "goal_type": "weight" if client.fitness_goal == "weight_loss" else "performance",
            "target_value": Decimal("65.00"),
            "current_value": Decimal("78.00"),
            "unit": "kg",
            "target_date": today + timedelta(days=90),
            "status": "active"
        }
    )

    months = {
    "August": (date(2025, 8, 1), date(2025, 8, 31)),
    "September": (date(2025, 9, 1), date(2025, 9, 30)),
    "October": (date(2025, 10, 1), date(2025, 10, 31)),
}

for client in clients:
    for month, (start, end) in months.items():
        # Random completed payment
        completed_day = start + timedelta(days=randint(0, (end - start).days))
        paid_day = completed_day + timedelta(days=randint(0, 3))  # paid 0-3 days after due
        Payment.objects.get_or_create(
            trainer=trainer,
            client=client,
            payment_type="monthly",
            amount=Decimal("2500.00"),
            currency="ETB",
            status="completed",
            due_date=completed_day,
            defaults={
                "paid_date": timezone.make_aware(datetime.combine(paid_day, datetime.now().time())),
                "description": f"Monthly coaching package - {month}",
                "notes": "Paid via cash or card"
            }
        )

        # Random pending payment
        pending_day = start + timedelta(days=randint(0, (end - start).days))
        Payment.objects.get_or_create(
            trainer=trainer,
            client=client,
            payment_type="session",
            amount=Decimal("400.00"),
            currency="ETB",
            status="pending",
            due_date=pending_day,
            defaults={
                "description": f"Upcoming session - {month}",
                "notes": "To be paid on due date"
            }
        )

print("✅ Payments generated for last 3 months for all clients.")

print("✅ Realistic payments, subscription, schedules, and progress goals seeded.")
 
 
 
 
import random
from datetime import timedelta
from django.utils import timezone
from decimal import Decimal
from apps.accounts.models import User
from apps.trainers.models import TrainerProfile
from apps.clients.models import ClientProfile
from apps.progress.models import ClientProgress

now = timezone.now()
today = now.date()
trainer = TrainerProfile.objects.get(user__username="trainerlayke")
clients = ClientProfile.objects.filter(trainer=trainer)

# Helper ranges
def random_weight(base):
    return round(base + random.uniform(-1.5, 1.2), 2)

def random_sleep():
    return round(random.uniform(5.5, 8.5), 1)

def random_measure(base):
    return round(base + random.uniform(-1.0, 1.0), 2)

def random_energy():
    return random.choice([2, 3, 4, 5])

def random_stress():
    return random.choice([1, 2, 3, 4])

notes_pool = [
    "Felt strong during squats.",
    "Low energy but pushed through.",
    "Slept well, good recovery.",
    "Skipped breakfast, felt sluggish.",
    "Great session, nailed form.",
    "Stressful day but workout helped.",
    "Tired but followed meal plan.",
    "Feeling leaner this week.",
    "Back pain slightly better.",
    "Mood was great, energy high."
]

feedback_pool = [
    "Keep up the consistency!",
    "Try to hydrate more on training days.",
    "Let’s increase protein intake slightly.",
    "Focus on sleep this week.",
    "Great job staying on track.",
    "Let’s adjust your mobility routine.",
    "Push harder on cardio next week.",
    "Recovery looks solid—keep it up.",
    "Add stretching post-session.",
    "You’re progressing well!"
]

for client in clients:
    base_weight = float(client.current_weight or 70.0)
    base_chest = 90.0
    base_waist = 80.0
    base_hip = 95.0
    base_arm = 30.0
    base_thigh = 55.0

    entry_count = random.randint(7, 12)
    for i in range(entry_count):
        entry_date = today - timedelta(days=random.randint(1, 30))
        if ClientProgress.objects.filter(client=client, date=entry_date).exists():
            continue

        ClientProgress.objects.create(
            client=client,
            date=entry_date,
            current_weight=random_weight(base_weight),
            workout_completed=random.choice([True, False]),
            meal_plan_followed=random.choice([True, False]),
            energy_level=random_energy(),
            sleep_hours=random_sleep(),
            stress_level=random_stress(),
            chest_measurement=random_measure(base_chest),
            waist_measurement=random_measure(base_waist),
            hip_measurement=random_measure(base_hip),
            arm_measurement=random_measure(base_arm),
            thigh_measurement=random_measure(base_thigh),
            notes=random.choice(notes_pool),
            trainer_feedback=random.choice(feedback_pool),
            created_at=timezone.now(),
            updated_at=timezone.now()
        )

print("✅ Detailed ClientProgress entries seeded for all clients.")


from django.utils import timezone
from decimal import Decimal
from apps.accounts.models import User
from apps.trainers.models import TrainerProfile
from apps.clients.models import ClientProfile
from apps.nutrition.models import MealPlan  # adjust import path if different

# ---- Configs ---------------------------------------------------------------

# Goal -> meal plan metadata (calories, macros, type, title)
GOAL_CONFIG = {
    "weight_loss": {
        "title": "Fasting Flex Plan",
        "meal_type": "weight_loss",
        "cal": 1800, "p": 120, "c": 180, "f": 60
    },
    "muscle_gain": {
        "title": "Bulking Boost",
        "meal_type": "muscle_gain",
        "cal": 2600, "p": 150, "c": 300, "f": 80
    },
    "strength": {
        "title": "Power Plate",
        "meal_type": "performance",
        "cal": 2400, "p": 150, "c": 260, "f": 75
    },
    "endurance": {
        "title": "Enduro Fuel",
        "meal_type": "performance",
        "cal": 2300, "p": 130, "c": 300, "f": 65
    },
    "flexibility": {
        "title": "Mobility Meals",
        "meal_type": "maintenance",
        "cal": 2100, "p": 115, "c": 240, "f": 70
    },
    "general_fitness": {
        "title": "Balanced Habesha Plate",
        "meal_type": "maintenance",
        "cal": 2200, "p": 120, "c": 250, "f": 70
    },
    "rehabilitation": {
        "title": "Recovery Nourishment",
        "meal_type": "therapeutic",
        "cal": 2100, "p": 120, "c": 230, "f": 70
    },
    "sports_performance": {
        "title": "Athlete’s Edge",
        "meal_type": "performance",
        "cal": 2500, "p": 140, "c": 300, "f": 75
    },
}

DAYS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
FASTING_DAYS = {"Wednesday", "Friday"}  # customize as needed

# Portion helper (approximate, easy to visualize)
# qty is approximate cooked weights or household measures
def non_fasting_day():
    return {
        "Breakfast": [
            {"name": "Kinche (cracked barley/oats) + flaxseed", "qty": "1 bowl (300g)"},
            {"name": "Boiled eggs", "qty": "2 pcs"},
            {"name": "Coffee or tea (unsweetened or light sugar)", "qty": "1 cup"}
        ],
        "Lunch": [
            {"name": "Injera", "qty": "2 rolls (~160g)"},
            {"name": "Doro Wot (chicken stew)", "qty": "150g"},
            {"name": "Gomen (collard greens)", "qty": "1 cup"},
            {"name": "Salad (tomato/onion/lettuce)", "qty": "1 cup"}
        ],
        "Dinner": [
            {"name": "Tibs (lean beef) or grilled fish", "qty": "150g"},
            {"name": "Injera or cooked rice", "qty": "1 roll or 1 cup"},
            {"name": "Atkilt (cabbage/carrot/potato mix)", "qty": "1 cup"}
        ],
        "Snacks": [
            {"name": "Telba (flaxseed drink) or plain yogurt", "qty": "1 cup"},
            {"name": "Fruit (banana/orange)", "qty": "1 pc"}
        ]
    }

def fasting_day():
    return {
        "Breakfast": [
            {"name": "Genfo (barley porridge) with shiro drizzle", "qty": "1 bowl (300g)"},
            {"name": "Black coffee/tea", "qty": "1 cup"}
        ],
        "Lunch": [
            {"name": "Injera", "qty": "2 rolls (~160g)"},
            {"name": "Shiro Wot (chickpea stew)", "qty": "1 cup"},
            {"name": "Gomen (collard greens)", "qty": "1 cup"},
            {"name": "Timatim salad", "qty": "1 cup"}
        ],
        "Dinner": [
            {"name": "Misir Wot (red lentil stew)", "qty": "1 cup"},
            {"name": "Injera", "qty": "1–2 rolls"},
            {"name": "Atkilt (cabbage/carrot/potato mix)", "qty": "1 cup"}
        ],
        "Snacks": [
            {"name": "Roasted chickpeas (kollo) or peanuts", "qty": "30–40g"},
            {"name": "Fruit (papaya or mango slice)", "qty": "1 serving"}
        ]
    }

# Adjustments for goals (simple swaps/boosts)
def adjust_for_goal(day_plan, goal):
    plan = {k: list(v) for k, v in day_plan.items()}
    if goal == "weight_loss":
        # Reduce starch at dinner; boost veggies
        plan["Dinner"] = [x for x in plan["Dinner"] if x["name"] not in ["Injera", "Injera or cooked rice"]]
        plan["Dinner"].append({"name": "Extra salad (lemon/olive oil light)", "qty": "1 cup"})
    elif goal == "muscle_gain":
        # Add protein snack and extra carb at lunch
        plan["Snacks"].append({"name": "Peanut butter on whole-grain bread", "qty": "1 slice"})
        plan["Lunch"].append({"name": "Extra rice or injera", "qty": "1 serving"})
    elif goal in ["strength", "sports_performance", "endurance"]:
        # Pre/post workout carb/protein emphasis
        plan["Snacks"].append({"name": "Atmit (fortified barley drink) post-workout", "qty": "1 cup"})
    elif goal == "flexibility":
        # Anti-inflammatory tilt (greens, legumes)
        plan["Dinner"].append({"name": "Extra gomen or kale sauté", "qty": "1 cup"})
    elif goal == "rehabilitation":
        # Gentle fiber and steady protein
        plan["Breakfast"].append({"name": "Oats with ground flax", "qty": "1 bowl"})
    # general_fitness already balanced
    return plan

def build_week(goal):
    week = {}
    for d in DAYS:
        base = fasting_day() if d in FASTING_DAYS else non_fasting_day()
        week[d] = adjust_for_goal(base, goal)
    return week

# ---- Main update logic ------------------------------------------------------

now = timezone.now()
trainer_user = User.objects.get(username="trainerlayke")
trainer = trainer_user.trainer_profile
clients = ClientProfile.objects.filter(trainer=trainer)

for client in clients:
    goal = client.fitness_goal or "general_fitness"
    cfg = GOAL_CONFIG.get(goal, GOAL_CONFIG["general_fitness"])

    # Find or create an active plan
    plan = client.meal_plans.filter(is_active=True).order_by("-created_at").first()
    if plan is None:
        plan = MealPlan(
            trainer=trainer,
            client=client,
            is_active=True,
            start_date=now.date()
        )

    plan.title = cfg["title"]
    plan.description = f"Ethiopian meal plan tailored for {goal.replace('_',' ').title()} with fasting-aware options."
    plan.meal_type = cfg["meal_type"]

    plan.daily_calories = cfg["cal"]
    plan.protein_grams = cfg["p"]
    plan.carbs_grams = cfg["c"]
    plan.fat_grams = cfg["f"]

    plan.meal_structure = build_week(goal)
    plan.includes_traditional_foods = True
    plan.fasting_considerations = "Follows Orthodox fasting on Wednesdays and Fridays (no animal products). Uses legumes (shiro, misir), whole grains (injera/teff, barley), and vegetables (gomen, atkilt)."

    plan.ai_enhanced = True
    plan.ai_suggestions = "Structured with energy timing, protein adequacy, and fasting compatibility. Adjust portions to individual appetite and progress."
    plan.save()

print("✅ Updated meal plans with Ethiopian, goal-aligned structures.")





from datetime import timedelta, date, time
from random import choice
from django.utils import timezone

from apps.accounts.models import User
from apps.clients.models import ClientProfile
from apps.schedules.models import WorkoutSchedule, WorkoutSession

# ── Setup ──
trainer_user = User.objects.get(username="trainerlayke")
trainer = trainer_user.trainer_profile

clients = ClientProfile.objects.filter(trainer=trainer, workout_plans__isnull=False).distinct()

# Possible start times
time_slots = [time(7, 0), time(9, 0), time(11, 0), time(15, 0), time(18, 0)]

# Generate schedules for August + September
start_date = date(2025, 8, 1)
end_date = date(2025, 9, 30)

for client in clients:
    plan = client.workout_plans.first()
    if not plan:
        continue

    # ── Create schedule ──
    schedule = WorkoutSchedule.objects.create(
        client=client,
        trainer=trainer,
        workout_plan=plan,
        weekly_sessions=client.weekly_sessions or 3,
        trainer_approve_required=True,
        start_date=start_date,
        end_date=end_date,
        default_start_time=choice(time_slots),
        default_duration=timedelta(hours=1),
        notes="Generated for August + September."
    )

    # ── Generate sessions ──
    schedule.generate_sessions()
    

print("✅ All workout schedules and sessions created for August + September.")


trainer = "trainerlayke"
trainer_profile = TrainerProfile.objects.get(user__username = trainer)

workout_plans = WorkoutPlan.objects.filter(trainer=trainer_profile)

for plan in workout_plans:
    client = plan.client
    structure = plan.workout_structure
    difficulty = plan.difficulty.lower()
    
    # Determine the number of past weeks to simulate
    weeks_to_simulate = 4
    
    # Adjust completion tendency based on difficulty
    if difficulty == 'beginner':
        completion_chance = 0.9
    elif difficulty == 'intermediate':
        completion_chance = 0.7
    else:  # advanced
        completion_chance = 0.5

    today = timezone.now().date()
    
    for week in range(weeks_to_simulate):
        week_offset = timedelta(weeks=week)
        
        # Randomize the days the client actually worked out this week
        for day_block in structure:
            available_days = [day_block['day']]
        workout_days_this_week = sample(available_days, min(client.weekly_sessions, len(available_days)))
        
        for day_name in workout_days_this_week:
            # Find the exercises for that day
            day_block = next(d for d in structure if d['day'] == day_name)
            exercises = day_block['exercises']
            for ex in exercises:
                # Randomly decide if exercise was completed
                if randint(1, 100) <= int(completion_chance * 100):
                    # Randomize the completion date within that week
                    completed_date = today - week_offset + timedelta(days=randint(0, 6))
            
                    ExerciseProgress.objects.get_or_create(
                        client=client,
                        workout_plan=plan,
                        day=day_name,
                        exercise_name=ex['name'],
                        defaults={'completed_at': timezone.make_aware(datetime.combine(completed_date, timezone.now().time()))}
                    )
    
    print(f"✅ Generated historical progress for {client.user.get_full_name()} - Plan: {plan.title}")

            
