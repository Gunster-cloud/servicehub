"""
Email Service for ServiceHub
"""

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails"""

    @staticmethod
    def send_welcome_email(user_email, user_name):
        """Send welcome email to new user"""
        try:
            subject = 'Bem-vindo ao ServiceHub!'
            context = {
                'user_name': user_name,
                'site_url': settings.SITE_URL,
            }
            
            html_message = render_to_string(
                'emails/welcome.html',
                context
            )
            
            send_mail(
                subject=subject,
                message=f'Bem-vindo ao ServiceHub, {user_name}!',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user_email],
                html_message=html_message,
                fail_silently=False,
            )
            
            logger.info(f'Welcome email sent to {user_email}')
            return True
        except Exception as e:
            logger.error(f'Error sending welcome email: {str(e)}')
            return False

    @staticmethod
    def send_quote_notification(client_email, quote_number, quote_value):
        """Send quote notification to client"""
        try:
            subject = f'Novo Orçamento #{quote_number}'
            context = {
                'quote_number': quote_number,
                'quote_value': quote_value,
                'site_url': settings.SITE_URL,
            }
            
            html_message = render_to_string(
                'emails/quote_notification.html',
                context
            )
            
            send_mail(
                subject=subject,
                message=f'Você recebeu um novo orçamento #{quote_number}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[client_email],
                html_message=html_message,
                fail_silently=False,
            )
            
            logger.info(f'Quote notification sent to {client_email}')
            return True
        except Exception as e:
            logger.error(f'Error sending quote notification: {str(e)}')
            return False

    @staticmethod
    def send_password_reset_email(user_email, reset_link):
        """Send password reset email"""
        try:
            subject = 'Redefinir sua senha'
            context = {
                'reset_link': reset_link,
                'site_url': settings.SITE_URL,
            }
            
            html_message = render_to_string(
                'emails/password_reset.html',
                context
            )
            
            send_mail(
                subject=subject,
                message=f'Clique no link para redefinir sua senha: {reset_link}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user_email],
                html_message=html_message,
                fail_silently=False,
            )
            
            logger.info(f'Password reset email sent to {user_email}')
            return True
        except Exception as e:
            logger.error(f'Error sending password reset email: {str(e)}')
            return False

    @staticmethod
    def send_admin_notification(subject, message, context=None):
        """Send notification to admins"""
        try:
            if context is None:
                context = {}
            
            html_message = render_to_string(
                'emails/admin_notification.html',
                context
            )
            
            admin_emails = [admin[1] for admin in settings.ADMINS]
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.SERVER_EMAIL,
                recipient_list=admin_emails,
                html_message=html_message,
                fail_silently=False,
            )
            
            logger.info(f'Admin notification sent: {subject}')
            return True
        except Exception as e:
            logger.error(f'Error sending admin notification: {str(e)}')
            return False

