from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from apps.messaging.models import EngagementMessage
from apps.clients.models import ClientProfile
from apps.progress.models import ClientProgress
from .services import ai_service

@shared_task
def send_daily_motivational_messages():
    """Send daily motivational messages to active clients"""
    
    # Get clients who should receive messages (active, with AI-enabled trainers)
    clients = ClientProfile.objects.filter(
        is_active=True,
        trainer__package__in=['pro', 'enterprise']  # AI features available
    )
    
    for client in clients:
        # Check if client already received a message today
        today = timezone.now().date()
        existing_message = EngagementMessage.objects.filter(
            client=client,
            created_at__date=today,
            message_type='motivational'
        ).exists()
        
        if not existing_message:
            # Get recent progress for context
            recent_progress = ClientProgress.objects.filter(
                client=client,
                date__gte=today - timedelta(days=7)
            ).order_by('-date')[:7]
            
            # Prepare data for AI
            client_info = {
                'name': client.user.first_name,
                'fitness_goal': client.get_fitness_goal_display(),
            }
            
            progress_data = {
                'recent_adherence': f"{len([p for p in recent_progress if p.workout_completed])}/{len(recent_progress)} workouts completed",
                'challenges': 'Maintaining consistency' if len(recent_progress) < 5 else 'Good progress'
            }
            
            # Generate AI message
            ai_message = ai_service.generate_motivational_message(client_info, progress_data)
            
            # Create and save message
            EngagementMessage.objects.create(
                trainer=client.trainer,
                client=client,
                subject="Daily Motivation",
                message=ai_message,
                message_type='motivational',
                ai_generated=True,
                sent_at=timezone.now()
            )

@shared_task
def send_weekly_progress_summaries():
    """Send weekly progress summaries to trainers"""
    
    # Get trainers with AI features
    from apps.trainers.models import TrainerProfile
    trainers = TrainerProfile.objects.filter(package__in=['pro', 'enterprise'])
    
    for trainer in trainers:
        # Get progress data for the past week
        week_ago = timezone.now().date() - timedelta(days=7)
        
        for client in trainer.clients.filter(is_active=True):
            progress_entries = ClientProgress.objects.filter(
                client=client,
                date__gte=week_ago
            ).order_by('-date')
            
            if progress_entries.exists():
                # Prepare data for AI summary
                client_info = {
                    'name': client.user.get_full_name(),
                    'fitness_goal': client.get_fitness_goal_display(),
                }
                
                progress_data = [
                    {
                        'date': str(entry.date),
                        'workout_completed': entry.workout_completed,
                        'meal_plan_followed': entry.meal_plan_followed,
                        'energy_level': entry.energy_level,
                        'weight': float(entry.current_weight) if entry.current_weight else None,
                        'notes': entry.notes
                    }
                    for entry in progress_entries
                ]
                
                # Generate AI summary
                ai_summary = ai_service.generate_progress_summary(client_info, progress_data)
                
                # Create message for trainer
                EngagementMessage.objects.create(
                    trainer=trainer,
                    client=client,
                    subject=f"Weekly Progress Summary - {client.user.get_full_name()}",
                    message=ai_summary,
                    message_type='check_in',
                    ai_generated=True,
                    sent_at=timezone.now()
                )

@shared_task
def send_payment_reminders():
    """Send payment reminders for overdue payments"""
    
    from apps.payments.models import Payment
    
    # Get overdue payments
    today = timezone.now().date()
    overdue_payments = Payment.objects.filter(
        status='pending',
        due_date__lt=today
    )
    
    for payment in overdue_payments:
        # Check if reminder was already sent today
        existing_reminder = EngagementMessage.objects.filter(
            client=payment.client,
            created_at__date=today,
            message_type='reminder',
            subject__icontains='payment'
        ).exists()
        
        if not existing_reminder:
            message = f"""
            Dear {payment.client.user.first_name},
            
            This is a friendly reminder that your payment for {payment.get_payment_type_display()} 
            of {payment.amount} {payment.currency} was due on {payment.due_date}.
            
            Please contact your trainer {payment.trainer.user.get_full_name()} to arrange payment.
            
            Thank you for your understanding.
            """
            
            EngagementMessage.objects.create(
                trainer=payment.trainer,
                client=payment.client,
                subject="Payment Reminder",
                message=message.strip(),
                message_type='reminder',
                priority='high',
                sent_at=timezone.now()
            )