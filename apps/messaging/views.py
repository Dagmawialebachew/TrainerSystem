from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy

from apps.core.mixins import TrainerRequiredMixin, TrainerOwnedMixin
from apps.trainers.models import TrainerProfile
from .models import EngagementMessage, MessageTemplate
from .forms import EngagementMessageForm, MessageTemplateForm

class MessageListView(LoginRequiredMixin, TrainerRequiredMixin, TrainerOwnedMixin, ListView):
    model = EngagementMessage
    template_name = 'messaging/list.html'
    context_object_name = 'messages'
    paginate_by = 20

class CreateMessageView(LoginRequiredMixin, TrainerRequiredMixin, CreateView):
    model = EngagementMessage
    form_class = EngagementMessageForm
    template_name = 'messaging/create.html'
    success_url = reverse_lazy('messaging:list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['trainer'] = get_object_or_404(TrainerProfile, user=self.request.user)
        return kwargs
    
    def form_valid(self, form):
        trainer_profile = get_object_or_404(TrainerProfile, user=self.request.user)
        form.instance.trainer = trainer_profile
        messages.success(self.request, 'Message created successfully!')
        return super().form_valid(form)

class MessageDetailView(LoginRequiredMixin, TrainerRequiredMixin, TrainerOwnedMixin, DetailView):
    model = EngagementMessage
    template_name = 'messaging/detail.html'
    context_object_name = 'message'

class TemplateListView(LoginRequiredMixin, TrainerRequiredMixin, TrainerOwnedMixin, ListView):
    model = MessageTemplate
    template_name = 'messaging/template_list.html'
    context_object_name = 'templates'
    paginate_by = 20

class CreateTemplateView(LoginRequiredMixin, TrainerRequiredMixin, CreateView):
    model = MessageTemplate
    form_class = MessageTemplateForm
    template_name = 'messaging/create_template.html'
    success_url = reverse_lazy('messaging:template_list')
    
    def form_valid(self, form):
        trainer_profile = get_object_or_404(TrainerProfile, user=self.request.user)
        form.instance.trainer = trainer_profile
        messages.success(self.request, 'Message template created successfully!')
        return super().form_valid(form)

class EditTemplateView(LoginRequiredMixin, TrainerRequiredMixin, TrainerOwnedMixin, UpdateView):
    model = MessageTemplate
    form_class = MessageTemplateForm
    template_name = 'messaging/edit_template.html'
    success_url = reverse_lazy('messaging:template_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Message template updated successfully!')
        return super().form_valid(form)