from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('', views.MessageListView.as_view(), name='list'),
    path('create/', views.CreateMessageView.as_view(), name='create'),
    path('<int:pk>/', views.MessageDetailView.as_view(), name='detail'),
    path('templates/', views.TemplateListView.as_view(), name='template_list'),
    path('templates/create/', views.CreateTemplateView.as_view(), name='create_template'),
    path('templates/<int:pk>/edit/', views.EditTemplateView.as_view(), name='edit_template'),
]