from django.urls import path
from . import views

app_name = 'schedule'

urlpatterns = [
    #Calendar
    path('calendar/', views.ScheduleCalendarView.as_view(), name='calendar'),

    # Schedule URLs
    path('', views.WorkoutScheduleListView.as_view(), name='list'),
    path('schedule/<int:pk>/', views.WorkoutScheduleDetailView.as_view(), name='detail'),
    path('schedule/add/', views.WorkoutScheduleCreateView.as_view(), name='add'),
    path('schedule/<int:pk>/edit/', views.WorkoutScheduleUpdateView.as_view(), name='edit'),
    path('schedule/<int:pk>/delete/', views.WorkoutScheduleDeleteView.as_view(), name='delete'),

    # Session URLs
    path('sessions/', views.WorkoutSessionListView.as_view(), name='session_list'),
    path('sessions/<int:pk>/', views.WorkoutSessionDetailView.as_view(), name='session_detail'),
    path('sessions/add/', views.WorkoutSessionCreateView.as_view(), name='session_add'),
path('sessions/<int:pk>/', views.WorkoutSessionDetailView.as_view(), name='session_detail'),

    # edit
    path('sessions/<int:pk>/edit/', views.WorkoutSessionUpdateView.as_view(), name='session_edit'),

    # approve
    path('sessions/<int:pk>/approve/', views.WorkoutSessionApproveView.as_view(), name='session_approve'),

    # reschedule (from modal)
    path('sessions/<int:pk>/reschedule/', views.WorkoutSessionRescheduleView.as_view(), name='session_reschedule'),
  path('sessions/<int:pk>/delete/', views.WorkoutSessionDeleteView.as_view(), name='session_delete'),

    # TimeBlock URLs
    path('timeblocks/', views.TimeBlockListView.as_view(), name='timeblock_list'),
    path('timeblocks/add/', views.TimeBlockCreateView.as_view(), name='timeblock_add'),
    path('timeblocks/<int:pk>/edit/', views.TimeBlockUpdateView.as_view(), name='timeblock_edit'),
    path('timeblocks/<int:pk>/delete/', views.TimeBlockDeleteView.as_view(), name='timeblock_delete'),
]
