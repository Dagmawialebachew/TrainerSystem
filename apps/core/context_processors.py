def branding_context(request):
    """Add branding context to all templates"""
    branding = getattr(request, 'branding', {
        'primary_color': '#3B82F6',
        'logo_url': None,
        'brand_name': 'FitnessSaaS',
    })
    
    return {
        'branding': branding,
    }