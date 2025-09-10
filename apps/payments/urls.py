from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.PaymentDashboardView.as_view(), name='dashboard'),
    path('create/', views.CreatePaymentView.as_view(), name='create'),
    path('<int:pk>/update/', views.PaymentUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.PaymentDeleteView.as_view(), name='delete'),
    path('<int:pk>/', views.PaymentDetailView.as_view(), name='detail'),
    path('subscription/', views.SubscriptionView.as_view(), name='subscription'),
    path('billing/', views.BillingHistoryView.as_view(), name='billing_history'),
     path('api/payments/revenue-trends/', views.RevenueTrendAPIView.as_view(), name='revenue-trends-api'),
     path('api/payments/client-payment-insights/', views.ClientPaymentInsightView.as_view(), name='client-payment-insights-api'),
]