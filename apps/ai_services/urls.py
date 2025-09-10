from django.urls import path
from . import views

app_name = 'ai_services'

urlpatterns = [
    path('workout/', views.WorkoutPlanAIView.as_view(), name='ai_workout'),
    path('meal/', views.MealPlanAIView.as_view(), name='ai_meal'),
    path('motivation/', views.MotivationMessageAIView.as_view(), name='ai_motivation'),
    path('summary/', views.ProgressSummaryAIView.as_view(), name='ai_summary'),
        path('', views.AIDashboardView.as_view(), name='ai_dashboard'),
            path('workout/generate/', views.GenerateAIWorkoutView.as_view(), name='generate_ai_workout'),
]

