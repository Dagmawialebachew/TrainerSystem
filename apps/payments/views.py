from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Count, Q

from apps.core.mixins import TrainerRequiredMixin,SubscriptionRequiredMixin, TrainerOwnedMixin
from apps.clients.models import ClientProfile
from .models import Payment, Subscription
from .forms import PaymentForm

class PaymentDashboardView(LoginRequiredMixin, TrainerRequiredMixin,SubscriptionRequiredMixin, TemplateView):
    template_name = 'payments/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        trainer_profile = get_object_or_404(TrainerProfile, user=self.request.user)
        
        # Payment statistics
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        
        payment_stats = Payment.objects.filter(
    trainer=trainer_profile,
    paid_date__date__gte=thirty_days_ago
).aggregate(
    total_revenue=Sum('amount'),
    completed_payments=Count('id', filter=Q(status='completed')),
    pending_payments=Count('id', filter=Q(status='pending'))
)
        
        # Recent payments
        recent_payments = Payment.objects.filter(
            trainer=trainer_profile
        ).order_by('-paid_date')[:10]
        
        # Subscription info
        subscription = getattr(trainer_profile, 'subscription', None)
        
        context.update({
            'trainer_profile': trainer_profile,
            'payment_stats': payment_stats,
            'recent_payments': recent_payments,
            'subscription': subscription,
        })
        
        return context

class CreatePaymentView(LoginRequiredMixin, TrainerRequiredMixin,SubscriptionRequiredMixin, CreateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'payments/create.html'
    success_url = reverse_lazy('payments:dashboard')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['trainer'] = get_object_or_404(TrainerProfile, user=self.request.user)
        return kwargs
    
    def form_valid(self, form):
        trainer_profile = get_object_or_404(TrainerProfile, user=self.request.user)
        form.instance.trainer = trainer_profile
        messages.success(self.request, 'Payment request created successfully!')
        return super().form_valid(form)

class PaymentDetailView(LoginRequiredMixin, TrainerRequiredMixin,SubscriptionRequiredMixin, TrainerOwnedMixin, DetailView):
    model = Payment
    template_name = 'payments/detail.html'
    context_object_name = 'payment'

class SubscriptionView(LoginRequiredMixin, TrainerRequiredMixin,SubscriptionRequiredMixin, TemplateView):
    template_name = 'payments/subscription.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        trainer_profile = get_object_or_404(TrainerProfile, user=self.request.user)
        subscription = getattr(trainer_profile, 'subscription', None)
        
        context.update({
            'trainer_profile': trainer_profile,
            'subscription': subscription,
        })
        
        return context
    
# views.py

class PaymentUpdateView(LoginRequiredMixin, TrainerRequiredMixin,SubscriptionRequiredMixin, TrainerOwnedMixin, UpdateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'payments/update.html'
    success_url = reverse_lazy('payments:billing_history')

    context_object_name = 'payment'
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['payment_type'].initial = self.get_object().payment_type
        return form

class PaymentDeleteView(LoginRequiredMixin, TrainerRequiredMixin,SubscriptionRequiredMixin, TrainerOwnedMixin, DeleteView):
    model = Payment
    template_name = 'payments/delete.html'
    success_url = reverse_lazy('payments:billing_history')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Payment deleted successfully!')
        return super().delete(request, *args, **kwargs)

class BillingHistoryView(LoginRequiredMixin, TrainerRequiredMixin,SubscriptionRequiredMixin, ListView):
    model = Payment
    template_name = 'payments/billing_history.html'
    context_object_name = 'payments'
    paginate_by = 10
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Payment.STATUS_CHOICES
        context['payment_type_choices'] = Payment.PAYMENT_TYPE_CHOICES
        print("context:", context['payment_type_choices'])
        
        return context
    
    def get_queryset(self):
        trainer_profile = get_object_or_404(TrainerProfile, user=self.request.user)
        queryset = Payment.objects.filter(trainer=trainer_profile).order_by('-updated_at')
        

        # Filtering
        status = self.request.GET.get('status')
        payment_type = self.request.GET.get('payment_type')
        search = self.request.GET.get('search')

        if status:
            queryset = queryset.filter(status=status)
        if payment_type:
            queryset = queryset.filter(payment_type=payment_type)
        if search:
            queryset = queryset.filter(
                Q(client__user__first_name__icontains=search) |
                Q(client__user__last_name__icontains=search) |
                Q(description__icontains=search)
            )

        return queryset
    
    
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum
from django.db.models.functions import TruncDate
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.payments.models import Payment

class RevenueTrendAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()
        start_date = today - timedelta(days=30)

        # Group payments by day using TruncDate
        daily_data = (
            Payment.objects
            .filter(status='completed', paid_date__isnull=False, trainer = request.user.trainer_profile)
            .annotate(day=TruncDate('paid_date'))
            .values('day')
            .annotate(total=Sum('amount'))
            .order_by('day')
        )

        labels = []
        values = []

        for entry in daily_data:
            labels.append(entry['day'].strftime('%b %d'))  #
            values.append(entry['total'])

        return Response({
            "labels": labels,
            "values": values
        })

        
from django.views import View
from django.http import JsonResponse
from django.db.models import Sum, Count
from apps.trainers.models import TrainerProfile
from apps.payments.models import Payment

class ClientPaymentInsightView(View):
        
    def get(self, request):
        # Revenue by status over time
        statuses = ['Paid', 'Pending', 'Failed']
        revenue_by_status = {status: [] for status in statuses}

        # Aggregate payments
        queryset = Payment.objects.filter(trainer = request.user.trainer_profile).values('paid_date', 'status').annotate(total=Sum('amount')).order_by('paid_date')

        # Safe list of dates (skip None)
        dates = sorted(set([entry['paid_date'].strftime('%b %d') for entry in queryset if entry['paid_date'] is not None]))
        labels = dates

        for date in dates:
            for status in statuses:
                total = sum(
                    entry['total']
                    for entry in queryset
                    if entry['paid_date'] is not None
                    and entry['paid_date'].strftime('%b %d') == date
                    and entry['status'] == status
                )
                revenue_by_status[status].append(total)



        # Top clients by revenue
        top_clients_qs = ClientProfile.objects.filter(trainer = request.user.trainer_profile).annotate(revenue=Sum('payments_made__amount')).order_by('-revenue')[:5]
        top_clients = [{"name": c.user.get_full_name(), "revenue": c.revenue or 0} for c in top_clients_qs]

        # Payment type breakdown
        payment_type_qs = Payment.objects.filter(trainer = request.user.trainer_profile).values('payment_type').annotate(count=Count('id'))
        total_payments = sum(p['count'] for p in payment_type_qs)
        payment_types = {
            p['payment_type']: round((p['count'] / total_payments) * 100)
            for p in payment_type_qs
        }

        # Total clients
        total_clients = ClientProfile.objects.count()


        return JsonResponse({
            "labels": labels,
            "revenue_by_status": revenue_by_status,
            "top_clients": top_clients,
            "payment_types": payment_types,
            "total_clients": total_clients
        })
