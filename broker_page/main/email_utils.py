import os
import ssl
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from datetime import datetime
import uuid
import traceback
from weasyprint import HTML
import tempfile


def send_welcome_email(user):
    """
    Send welcome email to newly registered user
    """
    try:
        subject = 'Welcome to Broker.Page!'
        
        # Render HTML email template
        html_content = render_to_string('emails/welcome_email.html', {
            'user': user,
        })
        
        # Create plain text version
        text_content = strip_tags(html_content)
        
        # Create email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]  # Send to user's email address
        )
        
        # Attach HTML content
        email.attach_alternative(html_content, "text/html")
        
        # Send email
        result = email.send()
        
        print(f"Welcome email sent successfully to {user.email}")
        return True
        
    except Exception as e:
        print(f"ERROR: Error sending welcome email to {user.email}: {str(e)}")
        print(f"ERROR: Full traceback:")
        traceback.print_exc()
        return False


def send_payment_confirmation_email(user, payment_id, order_id, amount):
    """
    Send payment confirmation email with PDF invoice attachment
    """
    try:
        subject = 'Payment Successful - Broker.Page Registration'
        
        # Generate invoice number
        invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Prepare context for payment confirmation email
        payment_context = {
            'user': user,
            'payment_id': payment_id,
            'order_id': order_id,
            'amount': amount,
            'payment_date': datetime.now().strftime('%B %d, %Y'),
        }
        
        # Render payment confirmation email template
        html_content = render_to_string('emails/payment_confirmation.html', payment_context)
        text_content = strip_tags(html_content)
        
        # Create email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]  # Send to user's email address
        )
        
        # Attach HTML content
        email.attach_alternative(html_content, "text/html")
        
        # Generate PDF invoice
        invoice_context = {
            'user': user,
            'invoice_number': invoice_number,
            'billed_date': datetime.now().strftime('%B %d, %Y'),
            'due_date': datetime.now().strftime('%B %d, %Y'),
            'payment_date': datetime.now().strftime('%B %d, %Y'),
            'amount': amount,
            'payment_id': payment_id,
            'order_id': order_id,
        }
        
        # Render invoice HTML
        invoice_html = render_to_string('emails/invoice_template.html', invoice_context)
        
        # Convert HTML to PDF
        pdf_content = HTML(string=invoice_html).write_pdf()
        
        # Attach PDF invoice
        email.attach(
            filename=f'Invoice-{invoice_number}.pdf',
            content=pdf_content,
            mimetype='application/pdf'
        )
        
        # Send email
        result = email.send()
        
        print(f"Payment confirmation email with PDF invoice sent successfully to {user.email}")
        return True
        
    except Exception as e:
        print(f"ERROR: Error sending payment confirmation email to {user.email}: {str(e)}")
        print(f"ERROR: Full traceback:")
        traceback.print_exc()
        return False


def send_test_email(test_email=None):
    """
    Send a test email to verify email configuration
    """
    try:
        subject = 'Test Email - Broker.Page'
        message = 'This is a test email to verify email configuration is working properly.'
        
        # Use provided test email or default
        to_email = test_email or 'broker.pagetest@gmail.com'
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email]
        )
        
        # Send email
        result = email.send()
        
        print(f"Test email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        print(f"ERROR: Error sending test email: {str(e)}")
        print(f"ERROR: Full traceback:")
        traceback.print_exc()
        return False 