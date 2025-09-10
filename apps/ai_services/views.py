from django.views.generic import FormView, TemplateView
from django.http import JsonResponse
from .services import ai_service

import logging
logger = logging.getLogger(__name__)

class AIDashboardView(TemplateView):
    template_name = 'ai_services/dashboard.html'

class WorkoutPlanAIView(FormView):
    template_name = 'ai_services/workout_result.html'
    success_url = '/ai/workout/'


    def post(self, request, *args, **kwargs):
        logger.info("Request body: %s", request.body)

        workout_data = {
            'days': request.POST.getlist('days'),
            'exercises': request.POST.getlist('exercises')
        }
        client_info = {
            'name': request.POST.get('name'),
            'fitness_goal': request.POST.get('goal'),
            'fitness_level': request.POST.get('level'),
            'equipment': request.POST.get('equipment'),
            'duration': int(request.POST.get('duration', 60))
        }
        result = ai_service.format_workout_plan(workout_data, client_info)
        return JsonResponse({'plan': result})


class MealPlanAIView(FormView):
    template_name = 'ai_services/meal_result.html'
    success_url = '/ai/meal/'

    def post(self, request, *args, **kwargs):
        meal_data = {
            'meals': request.POST.getlist('meals'),
            'snacks': request.POST.getlist('snacks')
        }
        client_info = {
            'name': request.POST.get('name'),
            'fitness_goal': request.POST.get('goal'),
            'dietary_restrictions': request.POST.get('restrictions'),
            'target_calories': request.POST.get('calories')
        }
        result = ai_service.format_meal_plan(meal_data, client_info)
        return JsonResponse({'plan': result})


class MotivationMessageAIView(FormView):
    template_name = 'ai_services/motivation_result.html'
    success_url = '/ai/motivation/'

    def post(self, request, *args, **kwargs):
        client_info = {
            'name': request.POST.get('name'),
            'fitness_goal': request.POST.get('goal')
        }
        progress_data = {
            'recent_adherence': request.POST.get('adherence'),
            'challenges': request.POST.get('challenges')
        }
        result = ai_service.generate_motivational_message(client_info, progress_data)
        return JsonResponse({'message': result})


class ProgressSummaryAIView(FormView):
    template_name = 'ai_services/summary_result.html'
    success_url = '/ai/summary/'

    def post(self, request, *args, **kwargs):
        client_info = {
            'name': request.POST.get('name'),
            'fitness_goal': request.POST.get('goal')
        }
        progress_entries = json.loads(request.POST.get('progress_entries', '[]'))
        result = ai_service.generate_progress_summary(client_info, progress_entries)
        return JsonResponse({'summary': result})



# views.py
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json

# Import your AI function
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from apps.ai_services.services import AIService




@method_decorator(csrf_exempt, name='dispatch')
class GenerateAIWorkoutView(View):
    def post(self, request, *args, **kwargs):
        try:
            # Decode the request body
            if not request.body:
                return JsonResponse({'error': 'No JSON data received'}, status=400)
            
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)  # <-- THIS is where JSONDecodeError occurs if body is empty
            print('Received data:', data)

            GOAL_MAP = {
                "muscle_gain": "Strength",
                "strength": "Strength",
                "fat_loss": "Cardio",
                "cardio": "Cardio"
            }

            difficulty = data.get('difficulty', 'Beginner').capitalize()
            goal = GOAL_MAP.get(data.get('goal', 'strength').lower(), "Strength")
            duration_weeks = data.get('duration_weeks', 4)
            days_per_week = data.get('days_per_week', 3)
            include_warmup_cooldown = data.get('include_warmup_cooldown', True)

            ai_service = AIService()
            workout_json = ai_service.ai_generate_workout(
                difficulty=difficulty,
                duration_weeks=duration_weeks,
                goal=goal,
                days_per_week=days_per_week,
                include_warmup_cooldown=include_warmup_cooldown
            )

            return JsonResponse({'workout_structure': workout_json})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'AI workout generation failed: {str(e)}'}, status=400)
