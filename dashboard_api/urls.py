from rest_framework.routers import DefaultRouter
from . import views
from django.urls import path

router = DefaultRouter()
router.register(r'schedules', views.WorkoutScheduleViewSet, basename='schedule')
router.register(r'sessions', views.WorkoutSessionViewSet, basename='session')
router.register(r'timeblocks', views.TimeBlockViewSet, basename='timeblock')

urlpatterns = [
    path("client-days/<int:client_id>/", views.ClientDaysView.as_view(), name="client-days"),
    path("summary/", views.EngagementSummaryView.as_view(), name="engagement_summary"),

]

urlpatterns += router.urls
