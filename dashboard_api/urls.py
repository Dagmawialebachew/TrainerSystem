from rest_framework.routers import DefaultRouter
from . import views
from django.urls import path
app_name = 'dashboard_api'

router = DefaultRouter()
router.register(r'schedules', views.WorkoutScheduleViewSet, basename='schedule')
router.register(r'sessions', views.WorkoutSessionViewSet, basename='session')
router.register(r'timeblocks', views.TimeBlockViewSet, basename='timeblock')

urlpatterns = [
    path("client-days/<int:client_id>/", views.ClientDaysView.as_view(), name="client-days"),
    path("summary/", views.EngagementSummaryView.as_view(), name="engagement_summary"),
    path('workout/complete/', views.WorkoutCompleteView.as_view(), name='api_workout_complete'),
    path('workout/complete/', views.WorkoutCompleteView.as_view(), name='complete'),
    path('workout/today/', views.TodayWorkoutView.as_view(), name='today'),
    path('motivation/', views.MotivationView.as_view(), name='motivation'),
    path('workout/analysis', views.WorkoutAnalyticsView.as_view(), name='analysis'),
    path('exercises/search/', views.ExerciseSearchView.as_view(), name='exercise_search'),

]

urlpatterns += router.urls
