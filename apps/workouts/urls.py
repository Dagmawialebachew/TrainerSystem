from django.urls import path
from . import views

app_name = 'workouts'

urlpatterns = [
    path('', views.WorkoutPlanListView.as_view(), name='list'),
    path('create/', views.CreateWorkoutPlanView.as_view(), name='create'),
    path('<int:pk>/', views.WorkoutPlanDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.EditWorkoutPlanView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.DeleteWorkoutPlanView.as_view(), name='delete'),
    path('exercises/', views.TrainerExerciseListView.as_view(), name='exercise_list'),
    path('exercises/add/', views.TrainerExerciseCreateView.as_view(), name='exercise_add'),
    path('exercises/<int:pk>/edit/', views.TrainerExerciseUpdateView.as_view(), name='exercise_edit'),
    path('exercises/<int:pk>/delete/', views.TrainerExerciseDeleteView.as_view(), name='exercise_delete'),
]

