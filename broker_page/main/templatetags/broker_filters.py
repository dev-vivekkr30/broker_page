from django import template
import re

register = template.Library()

@register.filter
def profile_slug(broker):
    """
    Generate a profile slug from broker's full name and mobile number
    Format: full-name-contact-number
    """
    if not broker.full_name or not broker.mobile:
        return ""
    
    # Clean the full name: remove special characters, convert to lowercase, replace spaces with hyphens
    name_slug = re.sub(r'[^a-zA-Z0-9\s-]', '', broker.full_name.lower())
    name_slug = re.sub(r'\s+', '-', name_slug.strip())
    
    # Clean the mobile number: remove any non-digit characters
    mobile_clean = re.sub(r'[^\d]', '', broker.mobile)
    
    return f"{name_slug}-{mobile_clean}"

@register.filter
def verification_count(broker):
    """
    Calculate the number of verified fields for a broker
    """
    verified_fields = [
        broker.is_name_verified,
        broker.is_photo_verified,
        broker.is_company_verified,
        broker.is_age_verified,
        broker.is_education_verified,
        broker.is_residence_colony_verified,
        broker.is_office_address_verified,
    ]
    return sum(verified_fields) 