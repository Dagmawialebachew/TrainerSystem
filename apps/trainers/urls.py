from django.urls import path
from . import views

app_name = 'trainers'

urlpatterns = [
    path('', views.TrainerDashboardView.as_view(), name='dashboard'),
    path('setup-profile/', views.SetupProfileView.as_view(), name='setup_profile'),
    path('profile/', views.TrainerProfileEditView.as_view(), name='profile'),
    path('clients/', views.ClientListView.as_view(), name='client_list'),
    path('clients/add/', views.AddClientView.as_view(), name='add_client'),
    path('clients/<int:pk>/', views.ClientDetailView.as_view(), name='client_detail'),
    path('clients/<int:pk>/edit/', views.ClientUpdateView.as_view(), name='edit_client'),  # <-- add this
    path('clients/<int:pk>/delete/', views.ClientDeleteView.as_view(), name='delete_client'),  # <-- add this

    path('analytics/', views.AnalyticsView.as_view(), name='analytics'),
    path('settings/', views.SettingsView.as_view(), name='settings'),
]