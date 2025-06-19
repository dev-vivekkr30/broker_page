#!/usr/bin/env python
"""
Check Razorpay payment details
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'broker_page.settings')
django.setup()

import razorpay
from django.conf import settings

def check_payment_details(payment_id):
    """Check payment details from Razorpay"""
    try:
        # Initialize Razorpay client
        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
        
        print(f"🔍 Checking payment details for: {payment_id}")
        print("=" * 50)
        
        # Fetch payment details
        payment_details = client.payment.fetch(payment_id)
        
        print("📊 Payment Details:")
        print(f"  - Payment ID: {payment_details.get('id')}")
        print(f"  - Status: {payment_details.get('status')}")
        print(f"  - Amount: {payment_details.get('amount')} paise (₹{payment_details.get('amount', 0)/100})")
        print(f"  - Currency: {payment_details.get('currency')}")
        print(f"  - Method: {payment_details.get('method')}")
        print(f"  - Email: {payment_details.get('email')}")
        print(f"  - Contact: {payment_details.get('contact')}")
        print(f"  - Created At: {payment_details.get('created_at')}")
        print(f"  - Captured At: {payment_details.get('captured_at')}")
        print(f"  - Description: {payment_details.get('description')}")
        print(f"  - Order ID: {payment_details.get('order_id')}")
        
        # Check if payment is captured
        if payment_details.get('status') == 'captured':
            print("✅ Payment is CAPTURED (successful)")
        elif payment_details.get('status') == 'authorized':
            print("⚠️  Payment is AUTHORIZED but not captured")
        elif payment_details.get('status') == 'failed':
            print("❌ Payment FAILED")
        else:
            print(f"❓ Payment status: {payment_details.get('status')}")
            
        return payment_details
        
    except Exception as e:
        print(f"❌ Error fetching payment details: {e}")
        return None

if __name__ == "__main__":
    payment_id = "pay_QiHDxMLtTpH72J"
    check_payment_details(payment_id) 