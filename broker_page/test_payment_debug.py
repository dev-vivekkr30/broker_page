#!/usr/bin/env python
"""
Test script to debug payment issues
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'broker_page.settings')
django.setup()

from main.models import Broker
import razorpay
from django.conf import settings

def test_razorpay_connection():
    """Test Razorpay connection"""
    try:
        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
        
        # Test creating a test order
        order_data = {
            'amount': 100000,  # ₹1000 in paise
            'currency': 'INR',
            'receipt': 'test_order_123',
            'payment_capture': '1'
        }
        
        order = client.order.create(order_data)
        print(f"✅ Razorpay connection successful")
        print(f"✅ Test order created: {order['id']}")
        return True
        
    except Exception as e:
        print(f"❌ Razorpay connection failed: {e}")
        return False

def check_existing_payments():
    """Check for existing payments in database"""
    payments = Broker.objects.filter(is_paid=True)
    print(f"📊 Found {payments.count()} paid users in database")
    
    for payment in payments:
        print(f"  - {payment.email}: {payment.razorpay_payment_id}")

def check_session_config():
    """Check session configuration"""
    print(f"🔧 Session Configuration:")
    print(f"  - SESSION_COOKIE_AGE: {getattr(settings, 'SESSION_COOKIE_AGE', 'Not set')}")
    print(f"  - SESSION_EXPIRE_AT_BROWSER_CLOSE: {getattr(settings, 'SESSION_EXPIRE_AT_BROWSER_CLOSE', 'Not set')}")
    print(f"  - SESSION_SAVE_EVERY_REQUEST: {getattr(settings, 'SESSION_SAVE_EVERY_REQUEST', 'Not set')}")

if __name__ == "__main__":
    print("🔍 Payment Debug Test")
    print("=" * 50)
    
    check_session_config()
    print()
    
    test_razorpay_connection()
    print()
    
    check_existing_payments()
    print()
    
    print("✅ Debug test completed") 