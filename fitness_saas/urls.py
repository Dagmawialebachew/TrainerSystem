"""
URL configuration for fitness_saas project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='landing.html'), name='home'),
    path('accounts/', include('apps.accounts.urls')),
    path('dashboard/', include('apps.trainers.urls')),
    path('client/', include('apps.clients.urls')),
    path('workouts/', include('apps.workouts.urls')),
    path('nutrition/', include('apps.nutrition.urls')),
    path('progress/', include('apps.progress.urls')),
    path('payments/', include('apps.payments.urls')),
    path('messaging/', include('apps.messaging.urls')),
    path('schedule/', include('apps.schedules.urls')),
    path('api/schedule/', include('dashboard_api.urls')), # API endpoints
    path("__reload__/", include("django_browser_reload.urls")),
    path("ai-services/", include("apps.ai_services.urls")),

]

# if notsettings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    