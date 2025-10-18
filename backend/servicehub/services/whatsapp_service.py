"""
WhatsApp Integration Service using Twilio
"""

from twilio.rest import Client
from django.conf import settings
from decouple import config
import logging

logger = logging.getLogger(__name__)


class WhatsAppService:
    """Service for sending WhatsApp messages via Twilio"""

    def __init__(self):
        self.account_sid = config('TWILIO_ACCOUNT_SID', default='')
        self.auth_token = config('TWILIO_AUTH_TOKEN', default='')
        self.whatsapp_number = config('TWILIO_WHATSAPP_NUMBER', default='')
        
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
        else:
            self.client = None

    def send_message(self, to_number, message):
        """Send WhatsApp message"""
        if not self.client:
            logger.error('Twilio client not configured')
            return False

        try:
            # Format phone number (add country code if needed)
            if not to_number.startswith('+'):
                to_number = f'+55{to_number}'

            message = self.client.messages.create(
                from_=f'whatsapp:{self.whatsapp_number}',
                body=message,
                to=f'whatsapp:{to_number}'
            )

            logger.info(f'WhatsApp message sent to {to_number}: {message.sid}')
            return True
        except Exception as e:
            logger.error(f'Error sending WhatsApp message: {str(e)}')
            return False

    def send_quote_notification(self, client_phone, quote_number, quote_value):
        """Send quote notification via WhatsApp"""
        message = f"""
Olá! 👋

Você recebeu um novo orçamento!

📋 Orçamento: #{quote_number}
💰 Valor: R$ {quote_value:.2f}

Clique no link para visualizar:
{settings.SITE_URL}/quotes/{quote_number}

Obrigado! 🙏
"""
        return self.send_message(client_phone, message)

    def send_quote_approval_notification(self, client_phone, quote_number):
        """Send quote approval notification via WhatsApp"""
        message = f"""
Ótimas notícias! 🎉

Seu orçamento #{quote_number} foi aprovado!

Entraremos em contato em breve para agendar o serviço.

Obrigado! 🙏
"""
        return self.send_message(client_phone, message)

    def send_service_completion_notification(self, client_phone, service_name):
        """Send service completion notification via WhatsApp"""
        message = f"""
Serviço Concluído! ✅

Seu serviço de {service_name} foi finalizado com sucesso!

Obrigado por confiar em nossos serviços! 🙏
"""
        return self.send_message(client_phone, message)

    def send_payment_reminder(self, client_phone, quote_number, amount):
        """Send payment reminder via WhatsApp"""
        message = f"""
Lembrete de Pagamento 💳

Orçamento: #{quote_number}
Valor: R$ {amount:.2f}

Clique no link para pagar:
{settings.SITE_URL}/payments/{quote_number}

Obrigado! 🙏
"""
        return self.send_message(client_phone, message)

    def send_appointment_reminder(self, client_phone, appointment_date, appointment_time):
        """Send appointment reminder via WhatsApp"""
        message = f"""
Lembrete de Agendamento 📅

Data: {appointment_date}
Horário: {appointment_time}

Nos vemos em breve! 👋
"""
        return self.send_message(client_phone, message)

    def send_bulk_message(self, phone_numbers, message):
        """Send message to multiple numbers"""
        results = []
        for phone in phone_numbers:
            result = self.send_message(phone, message)
            results.append({'phone': phone, 'success': result})
        
        return results

