# Email Setup Guide for Broker.Page

This guide explains how to set up and use the email functionality in the Broker.Page application.

## Features Implemented

1. **Welcome Email**: Sent automatically when a new user registers
2. **Payment Confirmation Email**: Sent when payment is successful, includes invoice attachment
3. **Invoice Generation**: Dynamic invoice generation with user details

## Email Configuration

### 1. Update Settings

Edit `broker_page/settings.py` and update the email configuration:

```python
# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Change to your email provider
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'broker.pagetest@gmail.com'  # Replace with your email
EMAIL_HOST_PASSWORD = 'zjuh tmps zkzz cact'  # Replace with your app password
DEFAULT_FROM_EMAIL = 'Broker.Page <broker.pagetest@gmail.com>'  # Replace with your email
```

### 2. Gmail Setup (Recommended)

If using Gmail:

1. Enable 2-Factor Authentication on your Gmail account
2. Generate an App Password:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate a new app password for "Mail"
   - Use this password in `EMAIL_HOST_PASSWORD`

### 3. Other Email Providers

For other providers, update the settings accordingly:

**Outlook/Hotmail:**
```python
EMAIL_HOST = 'smtp-mail.outlook.com'
EMAIL_PORT = 587
```

**Yahoo:**
```python
EMAIL_HOST = 'smtp.mail.yahoo.com'
EMAIL_PORT = 587
```

**Custom SMTP:**
```python
EMAIL_HOST = 'your-smtp-server.com'
EMAIL_PORT = 587  # or 465 for SSL
EMAIL_USE_SSL = True  # if using port 465
```

## Email Templates

The following email templates are located in `templates/emails/`:

1. **welcome_email.html**: Welcome email for new registrations
2. **payment_confirmation.html**: Payment success confirmation
3. **invoice_template.html**: Invoice template (attached to payment emails)

### Template Variables

**Welcome Email:**
- `user`: User object with all profile information

**Payment Confirmation Email:**
- `user`: User object
- `payment_id`: Razorpay payment ID
- `order_id`: Razorpay order ID
- `amount`: Payment amount
- `payment_date`: Payment date

**Invoice Template:**
- `user`: User object
- `invoice_number`: Generated invoice number
- `billed_date`: Invoice date
- `due_date`: Due date
- `payment_date`: Payment date
- `amount`: Payment amount

## Testing Email Functionality

### 1. Test Basic Email Configuration

```bash
python manage.py test_email --type test
```

### 2. Test Welcome Email

```bash
python manage.py test_email --type welcome --user-id 1
```

### 3. Test Payment Confirmation Email

```bash
python manage.py test_email --type payment --user-id 1
```

## Email Triggers

### Automatic Triggers

1. **User Registration**: Welcome email is sent automatically when a user completes registration
2. **Payment Success**: Payment confirmation email with invoice is sent when payment is verified

### Manual Triggers

You can manually trigger emails using the management command or by calling the functions directly:

```python
from main.email_utils import send_welcome_email, send_payment_confirmation_email

# Send welcome email
send_welcome_email(user)

# Send payment confirmation
send_payment_confirmation_email(
    user=user,
    payment_id='payment_123',
    order_id='order_456',
    amount=1000
)
```

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Check email and password in settings
   - Ensure 2FA is enabled and app password is used (for Gmail)
   - Verify SMTP settings for your provider

2. **Email Not Sending**
   - Check Django logs for error messages
   - Verify email configuration in settings
   - Test with management command

3. **Template Errors**
   - Ensure all template variables are provided
   - Check template syntax
   - Verify template paths

### Debug Mode

Enable debug mode to see detailed error messages:

```python
# In settings.py
DEBUG = True
```

### Logging

Add email logging to see what's happening:

```python
# In settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.core.mail': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## Production Considerations

1. **Use Environment Variables**: Store email credentials in environment variables
2. **Use Production SMTP**: Consider using services like SendGrid, Mailgun, or AWS SES
3. **Rate Limiting**: Implement rate limiting for email sending
4. **Error Handling**: Add proper error handling and retry logic
5. **Monitoring**: Set up monitoring for email delivery

### Environment Variables Example

```python
# In settings.py
import os

EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL')
```

## File Structure

```
broker_page/
├── main/
│   ├── email_utils.py          # Email utility functions
│   ├── management/
│   │   └── commands/
│   │       └── test_email.py   # Email testing command
│   └── views.py                # Updated with email triggers
├── templates/
│   └── emails/
│       ├── welcome_email.html
│       ├── payment_confirmation.html
│       └── invoice_template.html
└── broker_page/
    └── settings.py             # Email configuration
```

## Support

If you encounter issues:

1. Check the Django logs for error messages
2. Test email configuration with the management command
3. Verify SMTP settings with your email provider
4. Ensure all required dependencies are installed 