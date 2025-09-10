from openai import OpenAI
from django.conf import settings
from typing import Dict, Any
import json
from django.contrib import messages
from django.http import HttpRequest
from typing import Optional
import json
import logging
from typing import Dict, Any, Optional  # <- Optional is here
from django.conf import settings
from django.http import HttpRequest
from django.contrib import messages
from openai import OpenAI, APIError, RateLimitError, AuthenticationError
from typing import Optional
from django.http import HttpRequest
import logging
logger = logging.getLogger(__name__)
import random
EXERCISES = {
            "Beginner": {
                "Strength": ["Push-ups", "Bodyweight Squats", "Lunges", "Dumbbell Rows", "Plank"],
                "Cardio": ["Jumping Jacks", "High Knees", "Mountain Climbers", "Jog in Place"]
            },
            "Intermediate": {
                "Strength": ["Bench Press", "Deadlift", "Pull-ups", "Shoulder Press", "Leg Press"],
                "Cardio": ["Burpees", "Sprints", "Jump Rope", "Cycling"]
            },
            "Advanced": {
                "Strength": ["Clean and Jerk", "Front Squat", "Weighted Pull-ups", "Overhead Press"],
                "Cardio": ["HIIT Sprints", "Rowing", "Plyometric Jumps"]
            }
        }

WARMUP_EXERCISES = ["Arm Circles", "Leg Swings", "Light Jog 5 min", "Dynamic Stretching"]
COOLDOWN_EXERCISES = ["Static Stretching", "Foam Rolling", "Light Walk 5 min"]


class AIService:
    """Service for AI-powered features"""

    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def format_workout_plan(self, workout_data: Dict[str, Any], client_info: Dict[str, Any]) -> str:
        prompt = f"""
        You are a professional fitness trainer creating a workout plan for a client in Ethiopia.

        Client Information:
        - Name: {client_info.get('name', 'Client')}
        - Fitness Goal: {client_info.get('fitness_goal', 'General Fitness')}
        - Fitness Level: {client_info.get('fitness_level', 'Beginner')}
        - Available Equipment: {client_info.get('equipment', 'Minimal/Bodyweight')}
        - Workout Duration Preference: {client_info.get('duration', 60)} minutes

        Raw Workout Data:
        {json.dumps(workout_data, indent=2)}

        Please format this into a clear, structured workout plan that:
        1. Is culturally appropriate for Ethiopia
        2. Uses clear, simple language
        3. Includes proper warm-up and cool-down
        4. Provides exercise modifications for different fitness levels
        5. Includes rest periods and sets/reps
        6. Is motivating and encouraging
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception:
            return f"AI formatting unavailable. Original plan: {json.dumps(workout_data, indent=2)}"

    def format_meal_plan(self, meal_data: Dict[str, Any], client_info: Dict[str, Any]) -> str:
        prompt = f"""
        You are a nutritionist creating a meal plan for a client in Ethiopia.

        Client Information:
        - Name: {client_info.get('name', 'Client')}
        - Fitness Goal: {client_info.get('fitness_goal', 'General Fitness')}
        - Dietary Restrictions: {client_info.get('dietary_restrictions', 'None')}
        - Target Calories: {client_info.get('target_calories', 'Not specified')}
        - Cultural Considerations: Ethiopian cuisine, Orthodox fasting periods

        Raw Meal Data:
        {json.dumps(meal_data, indent=2)}

        Please format this into a comprehensive meal plan that:
        1. Incorporates traditional Ethiopian foods (injera, berbere, lentils, etc.)
        2. Respects Orthodox fasting traditions when applicable
        3. Uses locally available ingredients
        4. Provides portion sizes and preparation tips
        5. Includes healthy snack options
        6. Is culturally sensitive and practical
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception:
            return f"AI formatting unavailable. Original plan: {json.dumps(meal_data, indent=2)}"

    def generate_motivational_message(self, client_info: Dict[str, Any], progress_data: Dict[str, Any], request: Optional[HttpRequest] = None) -> str:
        """Generate personalized motivational message"""
        
        prompt = f"""
        You are a supportive fitness trainer in Ethiopia writing a motivational message to your client. (language both in amharic and english)
        
        Client Information:
        - Name: {client_info.get('name', 'Client')}
        - Fitness Goal: {client_info.get('fitness_goal', 'General Fitness')}
        - Recent Progress: {progress_data.get('recent_adherence', 'No recent data')}
        - Challenges: {progress_data.get('challenges', 'None noted')}
        
        Write a warm, encouraging message (2-3 sentences) that:
        1. Acknowledges their efforts
        2. Provides specific motivation related to their goal
        3. Is culturally appropriate for Ethiopia
        4. Includes practical encouragement
        5. Ends on a positive, action-oriented note
        
        Keep it personal, authentic, and motivating without being overly enthusiastic.
        """

        return self._chat_completion(prompt, request=request, max_tokens=200, temperature=0.8)
    
    

# Example exercises database

    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def ai_generate_workout(self, difficulty="Beginner", duration_weeks=4, goal="Strength",
                            days_per_week=3, include_warmup_cooldown=True):
        """
        Generate AI workout plan using OpenAI and return in front-end format:
        [
            {"day": "Monday", "exercises": [{"name":..., "sets":..., "reps":...}]},
            {"day": "Tuesday", ...}
        ]
        """
        WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        prompt = f"""
        You are a professional fitness trainer. Generate a {days_per_week}-day workout plan.
        Difficulty: {difficulty}
        Goal: {goal}
        Include warm-up and cool-down: {include_warmup_cooldown}

        Return ONLY valid JSON in this format:

        [
            {{
                "day": "Monday",
                "exercises": [
                    {{"name": "Push-ups", "sets": 3, "reps": 12}}
                ]
            }}
        ]
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000
            )

            raw = response.choices[0].message.content.strip()
            if not raw:
                raise ValueError("Empty AI response")

            # Remove code fences if present
            if raw.startswith("```"):
                raw = "\n".join(raw.split("\n")[1:-1]).strip()

            # Parse JSON
            workout_list = json.loads(raw)

            # Format for frontend
            formatted_plan = []
            for i, day_data in enumerate(workout_list):
                day_name = WEEKDAYS[i % 7]  # ensure unique weekdays
                exercises = [
                    {
                        "name": ex.get("name", ""),
                        "sets": ex.get("sets", 1),
                        "reps": ex.get("reps", 1)
                    } 
                    for ex in day_data.get("exercises", [])
                ]
                formatted_plan.append({"day": day_name, "exercises": exercises})

            return formatted_plan

        except json.JSONDecodeError as e:
            print("AI workout generation failed: JSON decode error", e)
            print("Raw AI output:", raw)
            return []
        except Exception as e:
            print("AI workout generation failed:", e)
            return []
        
        
    def generate_progress_summary(self, client_info: Dict[str, Any], progress_entries: list) -> str:
            prompt = f"""
            You are a fitness trainer analyzing your client's progress over the past week/month.

            Client: {client_info.get('name', 'Client')}
            Goal: {client_info.get('fitness_goal', 'General Fitness')}

            Progress Data:
            {json.dumps(progress_entries, indent=2)}

            Provide a concise progress summary that:
            1. Highlights key achievements and improvements
            2. Identifies areas for improvement
            3. Provides specific, actionable recommendations
            4. Is encouraging but honest
            5. Considers Ethiopian cultural context
            """

            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=300,
                    temperature=0.7
                )
                return response.choices[0].message.content
            except Exception:
                return "Progress summary unavailable. Please review the individual progress entries for detailed information."


    def _chat_completion(self, prompt: str, request: Optional[HttpRequest] = None, max_tokens: int = 500, temperature: float = 0.7) -> str:
        """Helper to safely call OpenAI API with error handling and user-friendly messages"""
        if not self.client:
            msg = "AI service unavailable. Please check API configuration."
            logger.error(msg)
            if request:
                messages.error(request, msg)
            return msg

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content

        except AuthenticationError:
            msg = "AI service authentication error. Please update API key."
            logger.error(msg)
            if request:
                messages.error(request, msg)
            return msg

        except RateLimitError:
            msg = "Too many requests to AI service. Try again in a few minutes."
            logger.warning(msg)
            if request:
                messages.warning(request, msg)
            return msg

        except APIError as e:
            msg = f"AI service error: {e}"
            logger.error(msg)
            if request:
                messages.error(request, "AI service is currently unavailable. Please try again later.")
            return "AI service is currently unavailable. Please try again later."

        except Exception as e:
            msg = f"Unexpected AI error: {e}"
            logger.exception(msg)
            if request:
                messages.error(request, "Unexpected error with AI service. Please try again later.")
            return "Unexpected AI error. Please try again later."

# Singleton instance
ai_service = AIService()
