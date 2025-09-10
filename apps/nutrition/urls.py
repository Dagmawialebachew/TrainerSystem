from django.urls import path
from . import views

app_name = 'nutrition'

urlpatterns = [
    path('', views.MealPlanListView.as_view(), name='list'),
    path('create/', views.CreateMealPlanView.as_view(), name='create'),
    path('<int:pk>/', views.MealPlanDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.EditMealPlanView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.DeleteMealPlanView.as_view(), name='delete'),
    # path('foods/', views.EthiopianFoodListView.as_view(), name='food_list'),
    # path('foods/<int:pk>/', views.EthiopianFoodDetailView.as_view(), name='food_detail'),
    
    path("foods/", views.TrainerFoodListView.as_view(), name="food_list"),
    path("foods/create/", views.TrainerFoodCreateView.as_view(), name="food_create"),
    path("foods/search/", views.TrainerFoodSearchView.as_view(), name="food_search"),
    path('foods/<int:pk>/edit/', views.TrainerFoodUpdateView.as_view(), name='food_edit'),
    path('foods/<int:pk>/delete/', views.DeleteTrainerFoodView.as_view(), name='food_delete'),
    
    path('search-foods/', views.TrainerFoodSearchView.as_view(), name='search_foods'),

]