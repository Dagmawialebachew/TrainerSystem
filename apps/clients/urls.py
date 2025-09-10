from django.urls import path
from . import views

app_name = 'clients'

urlpatterns = [
    path('', views.ClientDashboardView.as_view(), name='dashboard'),
    path('setup-profile/', views.ClientSetupProfileView.as_view(), name='setup_profile'),
    path('profile/', views.ClientEditProfileView.as_view(), name='profile'),
    path('workout-plan/', views.WorkoutPlanView.as_view(), name='workout_plan'),
    path('workout-plans/<int:pk>/', views.WorkoutPlanDetailView.as_view(), name='workout_plan_detail'),

    path('meal-plan/', views.MealPlanView.as_view(), name='meal_plan'),
    path('meal-plan/<int:pk>/', views.MealPlanDetailView.as_view(), name='meal_plan_detail'),

    path('progress/', views.ProgressView.as_view(), name='progress'),
    path('progress/log/', views.LogProgressView.as_view(), name='log_progress'),
    path('messages/', views.MessagesView.as_view(), name='messages'),
]