from django.utils.deprecation import MiddlewareMixin
from apps.trainers.models import TrainerProfile

class BrandingMiddleware(MiddlewareMixin):
    """Middleware to inject trainer branding into request context"""
    
    def process_request(self, request):
        # Default branding
        request.branding = {
            'primary_color': '#3B82F6',  # Blue
            'logo_url': None,
            'brand_name': 'FitnessSaaS',
        }
        
        # If user is a client, get their trainer's branding
        if (hasattr(request, 'user') and 
            request.user.is_authenticated and 
            hasattr(request.user, 'client_profile')):
            
            client_profile = request.user.client_profile
            if client_profile.trainer:
                trainer_profile = client_profile.trainer
                request.branding = {
                    'primary_color': trainer_profile.brand_color,
                    'logo_url': trainer_profile.logo.url if trainer_profile.logo else None,
                    'brand_name': trainer_profile.business_name or trainer_profile.user.get_full_name(),
                }
        
        # If user is a trainer, get their own branding
        elif (hasattr(request, 'user') and 
              request.user.is_authenticated and 
              hasattr(request.user, 'trainer_profile')):
            
            trainer_profile = request.user.trainer_profile
            request.branding = {
                'primary_color': trainer_profile.brand_color,
                'logo_url': trainer_profile.logo.url if trainer_profile.logo else None,
                'brand_name': trainer_profile.business_name or trainer_profile.user.get_full_name(),
            }