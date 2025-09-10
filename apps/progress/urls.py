from django.urls import path
from . import views

app_name = 'progress'

urlpatterns = [
    path('', views.ProgressOverviewView.as_view(), name='overview'),
    path('list/', views.ProgressListView.as_view(), name='list'),
    path('delete/<int:pk>/', views.DeleteProgressView.as_view(), name='delete'),
    path('goals/', views.GoalListView.as_view(), name='goal_list'),
    path('goals/create/', views.CreateGoalView.as_view(), name='create_goal'),
    path('goals/<int:pk>/', views.GoalDetailView.as_view(), name='goal_detail'),
    path('goals/<int:pk>/edit/', views.EditGoalView.as_view(), name='edit_goal'),
    path('goals/<int:pk>/delete/', views.DeleteGoalView.as_view(), name='delete_goal'),
    path('client/<int:client_pk>/progress/', views.ClientProgressView.as_view(), name='client_progress'),
        path('client/<int:client_pk>/progress/<int:entry_pk>/', views.ClientProgressView.as_view(), name='client_progress_detail'),

path('add/', views.CreateProgressView.as_view(), name='add_progress'),  # no client_pk
path('client/<int:client_pk>/add/', views.CreateProgressView.as_view(), name='add_progress'),  # with client_pk
    #API
        path('api/overview/', views.ProgressOverviewAPIView.as_view(), name='progress-overview-api'),
]