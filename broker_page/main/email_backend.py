import ssl
from django.core.mail.backends.smtp import EmailBackend as SMTPEmailBackend
import smtplib


class CustomSMTPEmailBackend(SMTPEmailBackend):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Create SSL context that doesn't verify certificates
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

    def open(self):
        if self.connection:
            return False
        
        connection_class = smtplib.SMTP_SSL if self.use_ssl else smtplib.SMTP
        kwargs = {}
        if self.timeout is not None:
            kwargs['timeout'] = self.timeout
        if self.use_ssl:
            kwargs['context'] = self.ssl_context
        try:
            self.connection = connection_class(self.host, self.port, **kwargs)
            if self.use_tls and not self.use_ssl:
                self.connection.starttls(context=self.ssl_context)
            if self.username:
                self.connection.login(self.username, self.password)
        except Exception:
            if not self.fail_silently:
                raise 