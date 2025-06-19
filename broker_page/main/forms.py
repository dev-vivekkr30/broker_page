# main/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Broker

class BrokerRegistrationForm(UserCreationForm):
    full_name = forms.CharField(label='Full Name')
    company = forms.CharField(label='Company/Firm Name')
    mobile = forms.CharField(label='Mobile Number')
    residence_colony = forms.CharField(label='Residence Colony')
    office_address = forms.CharField(widget=forms.Textarea, label='Office Address')
    about = forms.CharField(widget=forms.Textarea, required=False)
    age = forms.IntegerField(required=False)
    education = forms.CharField(required=False)
    expertise = forms.CharField(required=False, help_text='Comma-separated tags')
    whatsapp = forms.CharField(required=False)
    google_maps_url = forms.URLField(required=False)
    achievements = forms.CharField(widget=forms.Textarea, required=False)
    listings = forms.CharField(widget=forms.Textarea, required=False)
    min_deal_size = forms.CharField(required=False)
    max_deal_size = forms.CharField(required=False)
    profile_photo = forms.ImageField(required=False)
    profile_video = forms.FileField(required=False)
    facebook_url = forms.URLField(required=False)
    linkedin_url = forms.URLField(required=False)
    instagram_url = forms.URLField(required=False)
    twitter_url = forms.URLField(required=False)
    youtube_url = forms.URLField(required=False)
    website = forms.URLField(required=False)

    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        if mobile and Broker.objects.filter(mobile=mobile).exists():
            raise forms.ValidationError('A user with this mobile number already exists.')
        return mobile

    class Meta:
        model = Broker
        fields = ('email', 'password1', 'password2', 'full_name', 'company', 'mobile', 'residence_colony', 'office_address',
                  'about', 'age', 'education', 'expertise', 'whatsapp', 'google_maps_url', 'achievements', 'listings',
                  'min_deal_size', 'max_deal_size', 'profile_photo', 'profile_video', 'facebook_url', 'linkedin_url',
                  'instagram_url', 'twitter_url', 'youtube_url', 'website')