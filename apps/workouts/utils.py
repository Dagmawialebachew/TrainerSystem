from datetime import datetime
from apps.workouts.models import Exercise, ExerciseProgress
from django.utils import timezone

def enrich_workout_structure(workout_plan):
    """
    Take a WorkoutPlan instance and return a dict containing:
      - enriched workout_structure (with media + done flag)
      - exercise_map (for lookup)
      - current_day, client_id, plan_id, fitness_level
    """
    # 1. Raw JSON structure
    raw = (
        workout_plan.workout_structure
        if isinstance(workout_plan.workout_structure, list)
        else []
    )

    # 2. Fetch completed (day, exercise_name) tuples
    prog_qs = ExerciseProgress.objects.filter(
        client=workout_plan.client,
        workout_plan=workout_plan
    ).values_list('day', 'exercise_name')
    completed_set = set(prog_qs)

    # 3. Preload all active Exercise records
    all_exercises = Exercise.objects.filter(is_active=True)
    exercise_map = {e.name.lower(): e for e in all_exercises}

    # 4. Build enriched structure
    enriched = []
    for block in raw:
        day = block.get("day")
        items = []
        for ex in block.get("exercises", []):
            name = ex.get("name", "")
            key = (day, name)
            done = key in completed_set

            base = {
                "name": name,
                "sets": ex.get("sets"),
                "reps": ex.get("reps"),
                "done": done,
            }

            # attach media & metadata if available
            obj = exercise_map.get(name.lower())
            if obj:
                base.update({
                    "video_url": obj.demonstration_video_url or "",
                    "image_url": obj.image.url if obj.image else "",
                    "category": obj.category,
                    "equipment": obj.equipment_needed,
                    "difficulty": obj.difficulty_level,
                })

            items.append(base)

        enriched.append({"day": day, "exercises": items})
        print('this is passed the enriched', enriched)

    # 5. Return full context dict
    return {
        "workout_structure": enriched,
        "exercise_map": exercise_map,
        "current_day": timezone.localdate().strftime("%a"),
        "client_id": workout_plan.client.id,
        "plan_id": workout_plan.id,
        "fitness_level": workout_plan.difficulty,
    }

# workouts/utils.py
from datetime import date, timedelta

def compute_streak(progress_qs):
    days = set(progress_qs.values_list('completed_at__date', flat=True))
    streak, d = 0, date.today()
    while d in days:
        streak += 1
        d -= timedelta(days=1)
    return streak

def summarize_day_progress(structure, progress_qs, day_name):
    block = next((b for b in structure if b.get('day') == day_name), None)
    if not block:
        return {"completed": 0, "total": 0, "exercises": []}
    names = [e['name'] for e in block.get('exercises', [])]
    done = set(progress_qs.filter(day=day_name, exercise_name__in=names)
               .values_list('exercise_name', flat=True))
    exercises = []
    for ex in block.get('exercises', []):
        exercises.append({
            "name": ex['name'],
            "sets": ex.get('sets'),
            "reps": ex.get('reps'),
            "video_url": ex.get('video_url', ''),
            "done": ex['name'] in done
        })
    return {"completed": len(done), "total": len(names), "exercises": exercises}

