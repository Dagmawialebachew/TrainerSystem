from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('pending-approval/', views.PendingApprovalView.as_view(), name='pending_approval'),
    path('pending-payment/', views.PendingPaymentView.as_view(), name='pending_payment'),

]