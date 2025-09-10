# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AccountsUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()
    role = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=15)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_picture = models.CharField(max_length=100, blank=True, null=True)
    is_active_subscription = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'accounts_user'


class AccountsUserGroups(models.Model):
    user = models.ForeignKey(AccountsUser, models.DO_NOTHING)
    group = models.ForeignKey('AuthGroup', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'accounts_user_groups'
        unique_together = (('user', 'group'),)


class AccountsUserUserPermissions(models.Model):
    user = models.ForeignKey(AccountsUser, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'accounts_user_user_permissions'
        unique_together = (('user', 'permission'),)


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)
    name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class ClientsClientprofile(models.Model):
    fitness_goal = models.CharField(max_length=30)
    fitness_level = models.CharField(max_length=20)
    height = models.PositiveIntegerField(blank=True, null=True)
    current_weight = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    target_weight = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    dietary_restrictions = models.CharField(max_length=30)
    medical_conditions = models.TextField()
    allergies = models.TextField()
    preferred_workout_days = models.CharField(max_length=100)
    workout_duration_preference = models.PositiveIntegerField()
    is_active = models.BooleanField()
    start_date = models.DateField()
    notes = models.TextField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    trainer = models.ForeignKey('TrainersTrainerprofile', models.DO_NOTHING)
    user = models.OneToOneField(AccountsUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'clients_clientprofile'


class DjangoAdminLog(models.Model):
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AccountsUser, models.DO_NOTHING)
    action_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoCeleryBeatClockedschedule(models.Model):
    clocked_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_celery_beat_clockedschedule'


class DjangoCeleryBeatCrontabschedule(models.Model):
    minute = models.CharField(max_length=240)
    hour = models.CharField(max_length=96)
    day_of_week = models.CharField(max_length=64)
    day_of_month = models.CharField(max_length=124)
    month_of_year = models.CharField(max_length=64)
    timezone = models.CharField(max_length=63)

    class Meta:
        managed = False
        db_table = 'django_celery_beat_crontabschedule'


class DjangoCeleryBeatIntervalschedule(models.Model):
    every = models.IntegerField()
    period = models.CharField(max_length=24)

    class Meta:
        managed = False
        db_table = 'django_celery_beat_intervalschedule'


class DjangoCeleryBeatPeriodictask(models.Model):
    name = models.CharField(unique=True, max_length=200)
    task = models.CharField(max_length=200)
    args = models.TextField()
    kwargs = models.TextField()
    queue = models.CharField(max_length=200, blank=True, null=True)
    exchange = models.CharField(max_length=200, blank=True, null=True)
    routing_key = models.CharField(max_length=200, blank=True, null=True)
    expires = models.DateTimeField(blank=True, null=True)
    enabled = models.BooleanField()
    last_run_at = models.DateTimeField(blank=True, null=True)
    total_run_count = models.PositiveIntegerField()
    date_changed = models.DateTimeField()
    description = models.TextField()
    crontab = models.ForeignKey(DjangoCeleryBeatCrontabschedule, models.DO_NOTHING, blank=True, null=True)
    interval = models.ForeignKey(DjangoCeleryBeatIntervalschedule, models.DO_NOTHING, blank=True, null=True)
    solar = models.ForeignKey('DjangoCeleryBeatSolarschedule', models.DO_NOTHING, blank=True, null=True)
    one_off = models.BooleanField()
    start_time = models.DateTimeField(blank=True, null=True)
    priority = models.PositiveIntegerField(blank=True, null=True)
    headers = models.TextField()
    clocked = models.ForeignKey(DjangoCeleryBeatClockedschedule, models.DO_NOTHING, blank=True, null=True)
    expire_seconds = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'django_celery_beat_periodictask'


class DjangoCeleryBeatPeriodictasks(models.Model):
    ident = models.AutoField(primary_key=True)
    last_update = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_celery_beat_periodictasks'


class DjangoCeleryBeatSolarschedule(models.Model):
    event = models.CharField(max_length=24)
    latitude = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    longitude = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float

    class Meta:
        managed = False
        db_table = 'django_celery_beat_solarschedule'
        unique_together = (('event', 'latitude', 'longitude'),)


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class MessagingEngagementmessage(models.Model):
    subject = models.CharField(max_length=200)
    message = models.TextField()
    message_type = models.CharField(max_length=20)
    priority = models.CharField(max_length=10)
    scheduled_for = models.DateTimeField(blank=True, null=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    is_read = models.BooleanField()
    read_at = models.DateTimeField(blank=True, null=True)
    ai_generated = models.BooleanField()
    ai_prompt_used = models.TextField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    client = models.ForeignKey(ClientsClientprofile, models.DO_NOTHING)
    trainer = models.ForeignKey('TrainersTrainerprofile', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'messaging_engagementmessage'


class MessagingMessagetemplate(models.Model):
    name = models.CharField(max_length=100)
    subject_template = models.CharField(max_length=200)
    message_template = models.TextField()
    message_type = models.CharField(max_length=20)
    available_variables = models.JSONField()
    is_active = models.BooleanField()
    created_at = models.DateTimeField()
    trainer = models.ForeignKey('TrainersTrainerprofile', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'messaging_messagetemplate'


class NutritionEthiopianfood(models.Model):
    name = models.CharField(max_length=200)
    name_amharic = models.CharField(max_length=200)
    category = models.CharField(max_length=30)
    description = models.TextField()
    calories_per_100g = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    protein_per_100g = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    carbs_per_100g = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    fat_per_100g = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    fiber_per_100g = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    seasonal_availability = models.CharField(max_length=200)
    cultural_significance = models.TextField()
    preparation_notes = models.TextField()
    is_vegetarian = models.BooleanField()
    is_vegan = models.BooleanField()
    is_gluten_free = models.BooleanField()
    is_fasting_friendly = models.BooleanField()
    is_active = models.BooleanField()
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'nutrition_ethiopianfood'


class NutritionMealplan(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    meal_type = models.CharField(max_length=20)
    daily_calories = models.PositiveIntegerField(blank=True, null=True)
    protein_grams = models.PositiveIntegerField(blank=True, null=True)
    carbs_grams = models.PositiveIntegerField(blank=True, null=True)
    fat_grams = models.PositiveIntegerField(blank=True, null=True)
    meal_structure = models.JSONField()
    includes_traditional_foods = models.BooleanField()
    fasting_considerations = models.TextField()
    is_active = models.BooleanField()
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    ai_enhanced = models.BooleanField()
    ai_suggestions = models.TextField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    client = models.ForeignKey(ClientsClientprofile, models.DO_NOTHING)
    trainer = models.ForeignKey('TrainersTrainerprofile', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'nutrition_mealplan'


class NutritionTrainerfood(models.Model):
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=30)
    calories_per_100g = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    protein_per_100g = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    carbs_per_100g = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    fat_per_100g = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    is_active = models.BooleanField()
    created_at = models.DateTimeField()
    trainer = models.ForeignKey('TrainersTrainerprofile', models.DO_NOTHING)
    cultural_significance = models.TextField()
    description = models.TextField()
    fiber_per_100g = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    is_fasting_friendly = models.BooleanField()
    is_gluten_free = models.BooleanField()
    is_vegan = models.BooleanField()
    is_vegetarian = models.BooleanField()
    preparation_notes = models.TextField()
    seasonal_availability = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'nutrition_trainerfood'


class PaymentsPayment(models.Model):
    payment_type = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    currency = models.CharField(max_length=3)
    status = models.CharField(max_length=20)
    stripe_payment_intent_id = models.CharField(max_length=200)
    due_date = models.DateField()
    paid_date = models.DateTimeField(blank=True, null=True)
    description = models.TextField()
    notes = models.TextField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    client = models.ForeignKey(ClientsClientprofile, models.DO_NOTHING)
    trainer = models.ForeignKey('TrainersTrainerprofile', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'payments_payment'


class PaymentsSubscription(models.Model):
    package = models.CharField(max_length=20)
    status = models.CharField(max_length=20)
    monthly_amount = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    currency = models.CharField(max_length=3)
    stripe_subscription_id = models.CharField(max_length=200)
    start_date = models.DateTimeField()
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
    trial_end = models.DateTimeField(blank=True, null=True)
    cancelled_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    trainer = models.OneToOneField('TrainersTrainerprofile', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'payments_subscription'


class ProgressClientprogress(models.Model):
    date = models.DateField()
    current_weight = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    workout_completed = models.BooleanField()
    meal_plan_followed = models.BooleanField()
    energy_level = models.PositiveIntegerField(blank=True, null=True)
    sleep_hours = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    stress_level = models.PositiveIntegerField(blank=True, null=True)
    chest_measurement = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    waist_measurement = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    hip_measurement = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    arm_measurement = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    thigh_measurement = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    notes = models.TextField()
    trainer_feedback = models.TextField()
    progress_photo = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    client = models.ForeignKey(ClientsClientprofile, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'progress_clientprogress'
        unique_together = (('client', 'date'),)


class ProgressProgressgoal(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    goal_type = models.CharField(max_length=20)
    target_value = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    current_value = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    unit = models.CharField(max_length=20)
    target_date = models.DateField()
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    client = models.ForeignKey(ClientsClientprofile, models.DO_NOTHING)
    trainer = models.ForeignKey('TrainersTrainerprofile', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'progress_progressgoal'


class TrainersTrainerprofile(models.Model):
    business_name = models.CharField(max_length=100)
    bio = models.TextField()
    specializations = models.CharField(max_length=50)
    experience_years = models.PositiveIntegerField()
    certifications = models.TextField()
    package = models.CharField(max_length=20)
    package_start_date = models.DateTimeField()
    logo = models.CharField(max_length=100, blank=True, null=True)
    brand_color = models.CharField(max_length=7)
    address = models.TextField()
    city = models.CharField(max_length=50)
    website = models.CharField(max_length=200)
    instagram = models.CharField(max_length=100)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    is_accepting_clients = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    user = models.OneToOneField(AccountsUser, models.DO_NOTHING)
    is_verified = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'trainers_trainerprofile'


class WorkoutsExercise(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20)
    equipment_needed = models.CharField(max_length=30)
    muscle_groups = models.CharField(max_length=200)
    setup_instructions = models.TextField()
    execution_steps = models.TextField()
    safety_tips = models.TextField()
    demonstration_video_url = models.CharField(max_length=200)
    image = models.CharField(max_length=100, blank=True, null=True)
    difficulty_level = models.CharField(max_length=20)
    modifications = models.TextField()
    is_active = models.BooleanField()
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'workouts_exercise'


class WorkoutsWorkoutplan(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    difficulty = models.CharField(max_length=20)
    duration_weeks = models.PositiveIntegerField()
    workout_structure = models.JSONField()
    is_active = models.BooleanField()
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    ai_enhanced = models.BooleanField()
    ai_suggestions = models.TextField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    client = models.ForeignKey(ClientsClientprofile, models.DO_NOTHING)
    trainer = models.ForeignKey(TrainersTrainerprofile, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'workouts_workoutplan'
