# main/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class Colony(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Colonies"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class BrokerManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)

class Broker(AbstractUser):
    full_name = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    mobile = models.CharField(max_length=15)
    residence_colony = models.CharField(max_length=255)
    office_address = models.TextField()
    is_paid = models.BooleanField(default=False)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=100, blank=True, null=True)

    # Remove username field, use email instead
    username = None
    email = models.EmailField(unique=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = BrokerManager()

    about = models.TextField(blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    education = models.CharField(max_length=255, blank=True, null=True)
    expertise = models.CharField(max_length=512, blank=True, null=True)  # Comma-separated tags
    whatsapp = models.CharField(max_length=15, blank=True, null=True)
    google_maps_url = models.URLField(blank=True, null=True)
    achievements = models.TextField(blank=True, null=True)  # Comma-separated or JSON
    listings = models.TextField(blank=True, null=True)  # Comma-separated or JSON
    min_deal_size = models.CharField(max_length=50, blank=True, null=True)
    max_deal_size = models.CharField(max_length=50, blank=True, null=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    profile_video = models.FileField(upload_to='profile_videos/', blank=True, null=True)
    facebook_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    is_name_verified = models.BooleanField(default=False)
    is_photo_verified = models.BooleanField(default=False)
    is_company_verified = models.BooleanField(default=False)
    is_age_verified = models.BooleanField(default=False)
    is_education_verified = models.BooleanField(default=False)
    is_residence_colony_verified = models.BooleanField(default=False)
    is_office_address_verified = models.BooleanField(default=False)
    active_colonies = models.CharField(max_length=1024, blank=True, null=True)  # Comma-separated colonies/areas

    @property
    def is_fully_verified(self):
        return all([
            self.is_name_verified,
            self.is_photo_verified,
            self.is_company_verified,
            self.is_age_verified,
            self.is_education_verified,
            self.is_residence_colony_verified,
            self.is_office_address_verified,
        ])

    def __str__(self):
        return self.full_name if self.full_name else self.email