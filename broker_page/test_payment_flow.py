#!/usr/bin/env python
"""
Test script to simulate payment flow and identify issues
"""
import os
import django
import requests
from urllib.parse import urljoin

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'broker_page.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from main.models import Broker
import razorpay
from django.conf import settings

def test_payment_flow():
    """Test the complete payment flow"""
    print("🔍 Testing Payment Flow")
    print("=" * 50)
    
    # Create a test client
    client = Client()
    
    # Test 1: Check if thank_you URL is accessible
    print("1. Testing thank_you URL accessibility...")
    try:
        response = client.get(reverse('thank_you'))
        print(f"   ✅ thank_you URL accessible: {response.status_code}")
    except Exception as e:
        print(f"   ❌ thank_you URL error: {e}")
    
    # Test 2: Check if payment_failed URL is accessible
    print("2. Testing payment_failed URL accessibility...")
    try:
        response = client.get(reverse('payment_failed'))
        print(f"   ✅ payment_failed URL accessible: {response.status_code}")
    except Exception as e:
        print(f"   ❌ payment_failed URL error: {e}")
    
    # Test 3: Check Razorpay connection
    print("3. Testing Razorpay connection...")
    try:
        razorpay_client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
        print("   ✅ Razorpay client created successfully")
    except Exception as e:
        print(f"   ❌ Razorpay client error: {e}")
    
    # Test 4: Check existing payments
    print("4. Checking existing payments...")
    payments = Broker.objects.filter(is_paid=True)
    print(f"   📊 Found {payments.count()} paid users")
    for payment in payments:
        print(f"   - {payment.email}: {payment.razorpay_payment_id}")
    
    # Test 5: Check session configuration
    print("5. Checking session configuration...")
    print(f"   - SESSION_COOKIE_AGE: {getattr(settings, 'SESSION_COOKIE_AGE', 'Not set')}")
    print(f"   - SESSION_EXPIRE_AT_BROWSER_CLOSE: {getattr(settings, 'SESSION_EXPIRE_AT_BROWSER_CLOSE', 'Not set')}")
    print(f"   - SESSION_SAVE_EVERY_REQUEST: {getattr(settings, 'SESSION_SAVE_EVERY_REQUEST', 'Not set')}")
    
    print("=" * 50)
    print("✅ Payment flow test completed")

if __name__ == "__main__":
    test_payment_flow() 