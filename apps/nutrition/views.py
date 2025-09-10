import json
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from apps.nutrition.models import TrainerFood
from apps.nutrition.forms import TrainerFoodForm


from apps.core.mixins import TrainerRequiredMixin, TrainerOwnedMixin, SubscriptionRequiredMixin
from apps.trainers.models import TrainerProfile
from .models import MealPlan, EthiopianFood
from .forms import MealPlanForm

class MealPlanListView(LoginRequiredMixin, TrainerRequiredMixin, SubscriptionRequiredMixin, TrainerOwnedMixin, ListView):
    model = MealPlan
    template_name = 'nutrition/list.html'
    context_object_name = 'meal_plans'
    paginate_by = 20

class CreateMealPlanView(LoginRequiredMixin, CreateView):
    model = MealPlan
    form_class = MealPlanForm
    template_name = 'nutrition/create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        trainer_profile, _ = TrainerProfile.objects.get_or_create(user=self.request.user)
        context['trainer_foods'] = TrainerFood.objects.filter(trainer=trainer_profile, is_active=True)
        context['week_days'] = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
        context['meals'] = ['Breakfast','Lunch','Dinner','Snacks']
        context['plan'] = self.object
        return context
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs() 
        return kwargs
    def form_valid(self, form):
        trainer_profile, _ = TrainerProfile.objects.get_or_create(user=self.request.user)
        form.instance.trainer = trainer_profile
        # Save meal_structure JSON from POST
        meal_structure_raw = self.request.POST.get('meal_structure_json', '')
        print('meal_structure_raw',meal_structure_raw)
        form.instance.meal_structure = json.loads(meal_structure_raw)
        messages.success(self.request, 'Meal plan created successfully.')

        
        return super().form_valid(form)
        
class MealPlanDetailView(LoginRequiredMixin, TrainerRequiredMixin, SubscriptionRequiredMixin, TrainerOwnedMixin, DetailView):
    model = MealPlan
    template_name = 'nutrition/detail.html'
    context_object_name = 'meal_plan'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ensure meal_structure is a dict
        meal_structure = self.object.meal_structure
        print('This is the meal structure', meal_structure)
        if isinstance(meal_structure, str):
            try:
                meal_structure = json.loads(meal_structure)
            except json.JSONDecodeError:
                meal_structure = {}
        context['meal_structure'] = meal_structure
        
        # Optional: pass week_days and meals if you want to keep same structure as form
        context['week_days'] = list(meal_structure.keys()) if meal_structure else []
        context['meals'] = []
        if context['week_days']:
            first_day = context['week_days'][0]
            context['meals'] = list(meal_structure[first_day].keys()) if meal_structure[first_day] else []
        print('This is context passed to detail.html: ', context)

        return context
    
class EditMealPlanView(LoginRequiredMixin, TrainerRequiredMixin, SubscriptionRequiredMixin, TrainerOwnedMixin, UpdateView):
    model = MealPlan
    form_class = MealPlanForm
    template_name = 'nutrition/edit.html'
    success_url = reverse_lazy('nutrition:list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        meal_structure = self.object.meal_structure
        if isinstance(meal_structure, str):
            try:
                meal_structure = json.loads(meal_structure)
            except json.JSONDecodeError:
                meal_structure = {}

        # Ensure all days and meals exist for the form
        week_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        meals = ["Breakfast", "Lunch", "Dinner", "Snacks"]

        # Prefill missing days or meals
        structured_meals = []

        for day in week_days:
            day_meals = []
            for meal in meals:
                items = meal_structure.get(day, {}).get(meal, [])
                day_meals.append({
                    "meal": meal,
                    "items": items
                })
            structured_meals.append({
                "day": day,
                "meals": day_meals
            })

        context.update({ 
                       
            "structured_meals": structured_meals,
            "plan": self.object
        })
        print('This is the content being passed: ', context)

        return context
        
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['trainer'] = get_object_or_404(TrainerProfile, user=self.request.user)
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, 'Meal plan updated successfully!')
        trainer_profile, _ = TrainerProfile.objects.get_or_create(user=self.request.user)
        form.instance.trainer = trainer_profile
        # Save meal_structure JSON from POST
        meal_structure_raw = self.request.POST.get('meal_structure_json', '')
        print('meal_structure_raw',meal_structure_raw)
        form.instance.meal_structure = json.loads(meal_structure_raw)

        
        return super().form_valid(form)
        

class DeleteMealPlanView(LoginRequiredMixin, TrainerRequiredMixin, SubscriptionRequiredMixin, TrainerOwnedMixin, DeleteView):
    model = MealPlan
    template_name = 'nutrition/delete.html'
    success_url = reverse_lazy('nutrition:list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Meal plan deleted successfully!')
        return super().delete(request, *args, **kwargs)

class EthiopianFoodListView(LoginRequiredMixin, ListView):
    model = EthiopianFood
    template_name = 'nutrition/food_list.html'
    context_object_name = 'foods'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = EthiopianFood.objects.filter(is_active=True)
        
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        dietary = self.request.GET.get('dietary')
        if dietary == 'vegetarian':
            queryset = queryset.filter(is_vegetarian=True)
        elif dietary == 'vegan':
            queryset = queryset.filter(is_vegan=True)
        elif dietary == 'fasting':
            queryset = queryset.filter(is_fasting_friendly=True)
        
        return queryset.order_by('name')

class EthiopianFoodDetailView(LoginRequiredMixin, DetailView):
    model = EthiopianFood
    template_name = 'nutrition/food_detail.html'
    context_object_name = 'food'
    
    def get_queryset(self):
        return EthiopianFood.objects.filter(is_active=True)
    
    
    
    
class TrainerFoodListView(LoginRequiredMixin, ListView):
    model = TrainerFood
    template_name = "nutrition/food_list.html"
    context_object_name = "foods"

    def get_queryset(self):
        return TrainerFood.objects.filter(trainer=self.request.user.trainer_profile, is_active=True)


class TrainerFoodCreateView(LoginRequiredMixin, CreateView):
    model = TrainerFood
    form_class = TrainerFoodForm
    template_name = "nutrition/food_form.html"
    success_url = reverse_lazy("nutrition:food_list")  # <-- redirect after save



    def form_valid(self, form):
        trainer_profile, _ = TrainerProfile.objects.get_or_create(user=self.request.user)
        form.instance.trainer = trainer_profile
        return super().form_valid(form)


class TrainerFoodUpdateView(LoginRequiredMixin, TrainerRequiredMixin, SubscriptionRequiredMixin, TrainerOwnedMixin, UpdateView):
    model = TrainerFood
    form_class = TrainerFoodForm
    template_name = 'nutrition/food_edit.html'
    success_url = reverse_lazy('nutrition:food_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['trainer'] = get_object_or_404(TrainerProfile, user=self.request.user)
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Food item updated successfully!')
        return super().form_valid(form)
    
class DeleteTrainerFoodView(LoginRequiredMixin, TrainerRequiredMixin, SubscriptionRequiredMixin, TrainerOwnedMixin, DeleteView):
    model = TrainerFood
    template_name = 'nutrition/food_delete.html'
    success_url = reverse_lazy('nutrition:food_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Food item deleted successfully!')
        return super().delete(request, *args, **kwargs)


class TrainerFoodSearchView(LoginRequiredMixin, View):
    """AJAX search endpoint"""
    def get(self, request, *args, **kwargs):
        query = request.GET.get("q", "").strip()
        trainer_profile, _ = TrainerProfile.objects.get_or_create(user=self.request.user)

        foods = TrainerFood.objects.filter(
            trainer=trainer_profile,
            name__icontains=query,
            is_active=True
        )[:10]

        data = [
            {
                "id": food.id,
                "name": food.name,
                "calories": str(food.calories_per_100g or "N/A"),
                "protein": str(food.protein_per_100g or "N/A"),
                "carbs": str(food.carbs_per_100g or "N/A"),
                "fat": str(food.fat_per_100g or "N/A"),
            }
            for food in foods
        ]
        return JsonResponse(data, safe=False)