#!/usr/bin/env python
"""
Recover successful payment by creating user manually
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'broker_page.settings')
django.setup()

from main.models import Broker
import razorpay
from django.conf import settings

def recover_payment(payment_id):
    """Recover a successful payment by creating the user"""
    try:
        # Initialize Razorpay client
        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
        
        print(f"🔍 Recovering payment: {payment_id}")
        print("=" * 50)
        
        # Fetch payment details
        payment_details = client.payment.fetch(payment_id)
        
        if payment_details.get('status') != 'captured':
            print(f"❌ Payment is not captured. Status: {payment_details.get('status')}")
            return False
        
        email = payment_details.get('email')
        contact = payment_details.get('contact')
        order_id = payment_details.get('order_id')
        
        print(f"📊 Payment Details:")
        print(f"  - Email: {email}")
        print(f"  - Contact: {contact}")
        print(f"  - Order ID: {order_id}")
        print(f"  - Amount: ₹{payment_details.get('amount', 0)/100}")
        
        # Check if user already exists
        existing_user = Broker.objects.filter(email=email).first()
        if existing_user:
            print(f"❌ User already exists: {email}")
            return False
        
        # Check if payment ID already used
        existing_payment = Broker.objects.filter(razorpay_payment_id=payment_id).first()
        if existing_payment:
            print(f"❌ Payment ID already used: {payment_id}")
            return False
        
        # Create user with basic information
        # Note: We can only recover basic info from payment, other fields will be empty
        user = Broker.objects.create_user(
            email=email,
            password='temp_password_123',  # User will need to reset this
            full_name=email.split('@')[0],  # Basic name from email
            mobile=contact.replace('+91', '') if contact else '',
            company='',  # Will need to be filled manually
            residence_colony='',  # Will need to be filled manually
            office_address='',  # Will need to be filled manually
            is_paid=True,
            razorpay_payment_id=payment_id,
            razorpay_order_id=order_id,
            razorpay_signature='recovered_manual',  # Placeholder
        )
        
        print(f"✅ User created successfully:")
        print(f"  - User ID: {user.id}")
        print(f"  - Email: {user.email}")
        print(f"  - Is Paid: {user.is_paid}")
        print(f"  - Payment ID: {user.razorpay_payment_id}")
        
        print("\n⚠️  IMPORTANT:")
        print("  - User was created with temporary password: 'temp_password_123'")
        print("  - User should reset their password on first login")
        print("  - Profile information needs to be completed manually")
        
        return True
        
    except Exception as e:
        print(f"❌ Error recovering payment: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    payment_id = "pay_QiHDxMLtTpH72J"
    recover_payment(payment_id) 