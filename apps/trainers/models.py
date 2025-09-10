from django.db import models
from django.conf import settings
from django.urls import reverse

class TrainerProfile(models.Model):
    """Extended profile for trainers"""
    
    PACKAGE_CHOICES = [
        ('basic', 'Basic - $29/month'),
        ('pro', 'Pro - $79/month'),
        ('enterprise', 'Enterprise - $199/month'),
    ]
    
    SPECIALIZATION_CHOICES = [
        ('weight_loss', 'Weight Loss'),
        ('muscle_gain', 'Muscle Gain'),
        ('strength', 'Strength Training'),
        ('endurance', 'Endurance'),
        ('flexibility', 'Flexibility'),
        ('rehabilitation', 'Rehabilitation'),
        ('sports_specific', 'Sports Specific'),
        ('general_fitness', 'General Fitness'),
    ]
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='trainer_profile'
    )
    business_name = models.CharField(max_length=100)
    bio = models.TextField(max_length=500, help_text="Write a brief professional bio (max 500 characters). Highlight your expertise, achievements, and what makes you unique.")
    specializations = models.CharField(max_length=50, choices=SPECIALIZATION_CHOICES, default='general_fitness')
    experience_years = models.PositiveIntegerField(default=0)
    certifications = models.TextField(blank=True, help_text="List your certifications")
    is_paid = models.BooleanField(default=False)
    
    # SaaS Package
    package = models.CharField(max_length=20, choices=PACKAGE_CHOICES, default='basic')
    package_start_date = models.DateTimeField(auto_now_add=True)
    
    # Branding
    logo = models.ImageField(upload_to='trainer_logos/', null=True, blank=True)
    brand_color = models.CharField(max_length=7, default='#3B82F6', help_text="Hex color code")
    
    # Contact & Location
    address = models.TextField(blank=True)
    city = models.CharField(max_length=50, blank=True)
    website = models.URLField(blank=True)
    instagram = models.CharField(max_length=100, blank=True)
    
    # Settings
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    is_accepting_clients = models.BooleanField(default=True)
    
    #Verified
    is_verified = models.BooleanField(default=False)
    
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.business_name or 'Trainer'}"
    
    def get_absolute_url(self):
        return reverse('trainers:profile', kwargs={'pk': self.pk})
    
    @property
    def client_count(self):
        return self.clients.count()
    
    @property
    def can_add_clients(self):
        package_limits = settings.PACKAGE_LIMITS.get(self.package, {})
        max_clients = package_limits.get('max_clients', 0)
        return self.client_count < max_clients
    
    @property
    def has_ai_features(self):
        package_limits = settings.PACKAGE_LIMITS.get(self.package, {})
        return package_limits.get('ai_features', False)
    
    @property
    def has_custom_branding(self):
        package_limits = settings.PACKAGE_LIMITS.get(self.package, {})
        return package_limits.get('custom_branding', False)
    
    
    
    
    
# #from django.db import models
# from django.conf import settings
# from django.urls import reverse
# from datetime import timedelta
# from dateutil.relativedelta import relativedelta

# class TrainerProfile(models.Model):
#     """Extended profile for trainers with flexible billing."""

#     # 1. Core choices
#     PACKAGE_CHOICES = [
#         ('basic', 'Basic'),
#         ('pro', 'Pro'),
#         ('enterprise', 'Enterprise'),
#     ]
#     BILLING_INTERVAL_CHOICES = [
#         (1,  '1 month'),
#         (3,  '3 months'),
#         (6,  '6 months'),
#         (12, '12 months'),
#     ]

#     # 2. Pricing & discount maps
#     _MONTHLY_PRICING = {
#         'basic':      2000,   # currency units per month
#         'pro':        3000,
#         'enterprise': 7000,
#     }
#     _DISCOUNT_RATES = {
#         1:  0.00,   # no discount
#         3:  0.00,
#         6:  0.05,   # 5% off total
#         12: 0.10,   # 10% off total
#     }

#     # 3. Fields
#     user               = models.OneToOneField(settings.AUTH_USER_MODEL,
#                                               on_delete=models.CASCADE,
#                                               related_name='trainer_profile')
#     business_name      = models.CharField(max_length=100)
#     bio                = models.TextField(max_length=500)
#     specializations    = models.CharField(max_length=50,
#                                           choices=settings.SPECIALIZATION_CHOICES,
#                                           default='general_fitness')
#     experience_years   = models.PositiveIntegerField(default=0)
#     certifications     = models.TextField(blank=True, help_text="List your certifications")
#     is_verified        = models.BooleanField(default=False)

#     # SaaS subscription
#     package            = models.CharField(max_length=20,
#                                           choices=PACKAGE_CHOICES,
#                                           default='basic')
#     billing_interval   = models.PositiveSmallIntegerField(
#                             choices=BILLING_INTERVAL_CHOICES,
#                             default=1,
#                             help_text="Select how many months you pre-pay for"
#                         )
#     package_start_date = models.DateTimeField(auto_now_add=True)

#     # Branding & contact
#     logo               = models.ImageField(upload_to='trainer_logos/',
#                                            null=True, blank=True)
#     brand_color        = models.CharField(max_length=7,
#                                           default='#3B82F6',
#                                           help_text="Hex color code")
#     address            = models.TextField(blank=True)
#     city               = models.CharField(max_length=50, blank=True)
#     website            = models.URLField(blank=True)
#     instagram          = models.CharField(max_length=100, blank=True)

#     # Operational settings
#     hourly_rate        = models.DecimalField(max_digits=6,
#                                              decimal_places=2,
#                                              default=0.00)
#     is_accepting_clients = models.BooleanField(default=True)

#     created_at         = models.DateTimeField(auto_now_add=True)
#     updated_at         = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"{self.user.get_full_name()} – {self.business_name or 'Trainer'}"

#     def get_absolute_url(self):
#         return reverse('trainers:profile', kwargs={'pk': self.pk})

#     #
#     # ─── BILLING PROPERTIES ───────────────────────────────────────────────────────
#     #

#     @property
#     def monthly_fee(self) -> int:
#         """Base price per single month for this package."""
#         return self._MONTHLY_PRICING.get(self.package, 0)

#     @property
#     def interval_months(self) -> int:
#         """Number of months in the chosen billing interval."""
#         return int(self.billing_interval)

#     @property
#     def discount_rate(self) -> float:
#         """Discount fraction applied for multi-month pre-pays."""
#         return self._DISCOUNT_RATES.get(self.interval_months, 0.0)

#     @property
#     def total_fee(self) -> float:
#         """
#         Total due for this cycle:
#         (monthly_fee × interval_months) minus discount.
#         """
#         base = self.monthly_fee * self.interval_months
#         return round(base * (1 - self.discount_rate), 2)

#     @property
#     def renewal_date(self):
#         """
#         When the current cycle ends:
#         adds billing_interval months to package_start_date.
#         """
#         return self.package_start_date + relativedelta(months=self.interval_months)

#     @property
#     def is_active_subscription(self) -> bool:
#         """True if today is before the renewal_date."""
#         from django.utils import timezone
#         return timezone.now() < self.renewal_date

#     #
#     # ─── CLIENT & FEATURE HELPERS ────────────────────────────────────────────────
#     #

#     @property
#     def client_count(self) -> int:
#         return self.clients.count()

#     @property
#     def can_add_clients(self) -> bool:
#         limits = settings.PACKAGE_LIMITS.get(self.package, {})
#         return self.client_count < limits.get('max_clients', 0)

#     @property
#     def has_ai_features(self) -> bool:
#         return settings.PACKAGE_LIMITS.get(self.package, {}).get('ai_features', False)

#     @property
#     def has_custom_branding(self) -> bool:
#         return settings.PACKAGE_LIMITS.get(self.package, {}).get('custom_branding', False)
#     #