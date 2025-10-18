"""
Email Configuration for ServiceHub
"""

import os
from decouple import config

# Email Backend
EMAIL_BACKEND = config(
    'EMAIL_BACKEND',
    default='django.core.mail.backends.console.EmailBackend'
)

# SMTP Configuration
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# Default email sender
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@servicehub.com.br')
SERVER_EMAIL = config('SERVER_EMAIL', default='server@servicehub.com.br')

# Email templates
EMAIL_TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), '..', 'templates', 'emails')

# Anymail configuration (optional, for advanced email handling)
ANYMAIL = {
    'MAILGUN_API_KEY': config('MAILGUN_API_KEY', default=''),
    'MAILGUN_SENDER_DOMAIN': config('MAILGUN_SENDER_DOMAIN', default=''),
}

# Email notifications
SEND_ADMIN_EMAILS = config('SEND_ADMIN_EMAILS', default=True, cast=bool)
ADMINS = [
    ('Admin', 'admin@servicehub.com.br'),
]
MANAGERS = ADMINS

