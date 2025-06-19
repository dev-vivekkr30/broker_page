from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from main.email_utils import send_test_email, send_welcome_email, send_payment_confirmation_email

User = get_user_model()

class Command(BaseCommand):
    help = 'Test email functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            choices=['test', 'welcome', 'payment'],
            default='test',
            help='Type of email to test'
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Email address to send test email to'
        )
        parser.add_argument(
            '--user-id',
            type=int,
            help='User ID to send welcome/payment email to'
        )

    def handle(self, *args, **options):
        email_type = options['type']
        
        if email_type == 'test':
            test_email = options['email']
            self.stdout.write(f'Sending test email to {test_email or "default email"}...')
            success = send_test_email(test_email)
            if success:
                self.stdout.write(self.style.SUCCESS('Test email sent successfully!'))
            else:
                self.stdout.write(self.style.ERROR('Failed to send test email'))
                
        elif email_type == 'welcome':
            user_id = options['user_id']
            if not user_id:
                self.stdout.write(self.style.ERROR('Please provide --user-id for welcome email'))
                return
                
            try:
                user = User.objects.get(id=user_id)
                self.stdout.write(f'Sending welcome email to {user.email}...')
                success = send_welcome_email(user)
                if success:
                    self.stdout.write(self.style.SUCCESS('Welcome email sent successfully!'))
                else:
                    self.stdout.write(self.style.ERROR('Failed to send welcome email'))
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'User with ID {user_id} not found'))
                
        elif email_type == 'payment':
            user_id = options['user_id']
            if not user_id:
                self.stdout.write(self.style.ERROR('Please provide --user-id for payment email'))
                return
                
            try:
                user = User.objects.get(id=user_id)
                self.stdout.write(f'Sending payment confirmation email to {user.email}...')
                success = send_payment_confirmation_email(
                    user=user,
                    payment_id='test_payment_123',
                    order_id='test_order_456',
                    amount=1000
                )
                if success:
                    self.stdout.write(self.style.SUCCESS('Payment confirmation email sent successfully!'))
                else:
                    self.stdout.write(self.style.ERROR('Failed to send payment confirmation email'))
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'User with ID {user_id} not found')) 