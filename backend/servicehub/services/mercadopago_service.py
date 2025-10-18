"""
Mercado Pago Integration Service
"""

import mercadopago
from django.conf import settings
from decouple import config
import logging

logger = logging.getLogger(__name__)

# Mercado Pago Configuration
MERCADOPAGO_ACCESS_TOKEN = config('MERCADOPAGO_ACCESS_TOKEN', default='')
MERCADOPAGO_PUBLIC_KEY = config('MERCADOPAGO_PUBLIC_KEY', default='')


class MercadoPagoService:
    """Service for Mercado Pago payments"""

    def __init__(self):
        self.access_token = MERCADOPAGO_ACCESS_TOKEN
        if self.access_token:
            self.sdk = mercadopago.SDK(self.access_token)
        else:
            self.sdk = None

    def create_preference(self, items, payer_info=None, metadata=None):
        """Create a Mercado Pago preference"""
        if not self.sdk:
            logger.error('Mercado Pago SDK not configured')
            return None

        try:
            preference_data = {
                'items': items,
                'back_urls': {
                    'success': f'{settings.SITE_URL}/payments/success',
                    'failure': f'{settings.SITE_URL}/payments/failure',
                    'pending': f'{settings.SITE_URL}/payments/pending',
                },
                'auto_return': 'approved',
                'notification_url': f'{settings.SITE_URL}/api/v1/payments/mercadopago/webhook/',
            }

            if payer_info:
                preference_data['payer'] = payer_info

            if metadata:
                preference_data['metadata'] = metadata

            result = self.sdk.preference().create(preference_data)

            if result['status'] == 201:
                logger.info(f'Mercado Pago preference created: {result["response"]["id"]}')
                return result['response']
            else:
                logger.error(f'Mercado Pago error: {result}')
                return None
        except Exception as e:
            logger.error(f'Mercado Pago error: {str(e)}')
            return None

    def create_quote_preference(self, quote, client):
        """Create preference for quote payment"""
        items = [
            {
                'title': f'Orçamento #{quote.id}',
                'description': quote.description or 'Serviço',
                'quantity': 1,
                'unit_price': float(quote.total_value),
            }
        ]

        payer_info = {
            'name': client.name,
            'email': client.email,
            'phone': {
                'area_code': '11',
                'number': client.phone.replace('-', '').replace(' ', '') if client.phone else '',
            },
            'address': {
                'street_name': client.address or '',
                'street_number': '',
                'zip_code': client.postal_code or '',
            },
        }

        metadata = {
            'quote_id': quote.id,
            'client_id': client.id,
            'quote_number': quote.number,
        }

        return self.create_preference(items, payer_info, metadata)

    def get_payment(self, payment_id):
        """Get payment details"""
        if not self.sdk:
            logger.error('Mercado Pago SDK not configured')
            return None

        try:
            result = self.sdk.payment().get(payment_id)

            if result['status'] == 200:
                logger.info(f'Mercado Pago payment retrieved: {payment_id}')
                return result['response']
            else:
                logger.error(f'Mercado Pago error: {result}')
                return None
        except Exception as e:
            logger.error(f'Mercado Pago error: {str(e)}')
            return None

    def cancel_payment(self, payment_id):
        """Cancel a payment"""
        if not self.sdk:
            logger.error('Mercado Pago SDK not configured')
            return False

        try:
            result = self.sdk.payment().update(
                payment_id,
                {'status': 'cancelled'}
            )

            if result['status'] == 200:
                logger.info(f'Mercado Pago payment cancelled: {payment_id}')
                return True
            else:
                logger.error(f'Mercado Pago error: {result}')
                return False
        except Exception as e:
            logger.error(f'Mercado Pago error: {str(e)}')
            return False

    def refund_payment(self, payment_id, amount=None):
        """Refund a payment"""
        if not self.sdk:
            logger.error('Mercado Pago SDK not configured')
            return None

        try:
            refund_data = {}
            if amount:
                refund_data['amount'] = float(amount)

            result = self.sdk.refund().create(payment_id, refund_data)

            if result['status'] == 201:
                logger.info(f'Mercado Pago refund created: {result["response"]["id"]}')
                return result['response']
            else:
                logger.error(f'Mercado Pago error: {result}')
                return None
        except Exception as e:
            logger.error(f'Mercado Pago error: {str(e)}')
            return None

    def create_subscription(self, payer_email, plan_id, metadata=None):
        """Create a subscription plan"""
        if not self.sdk:
            logger.error('Mercado Pago SDK not configured')
            return None

        try:
            subscription_data = {
                'payer_email': payer_email,
                'plan_id': plan_id,
            }

            if metadata:
                subscription_data['metadata'] = metadata

            result = self.sdk.subscription().create(subscription_data)

            if result['status'] == 201:
                logger.info(f'Mercado Pago subscription created: {result["response"]["id"]}')
                return result['response']
            else:
                logger.error(f'Mercado Pago error: {result}')
                return None
        except Exception as e:
            logger.error(f'Mercado Pago error: {str(e)}')
            return None

    def get_subscription(self, subscription_id):
        """Get subscription details"""
        if not self.sdk:
            logger.error('Mercado Pago SDK not configured')
            return None

        try:
            result = self.sdk.subscription().get(subscription_id)

            if result['status'] == 200:
                logger.info(f'Mercado Pago subscription retrieved: {subscription_id}')
                return result['response']
            else:
                logger.error(f'Mercado Pago error: {result}')
                return None
        except Exception as e:
            logger.error(f'Mercado Pago error: {str(e)}')
            return None

    def cancel_subscription(self, subscription_id):
        """Cancel a subscription"""
        if not self.sdk:
            logger.error('Mercado Pago SDK not configured')
            return False

        try:
            result = self.sdk.subscription().update(
                subscription_id,
                {'status': 'cancelled'}
            )

            if result['status'] == 200:
                logger.info(f'Mercado Pago subscription cancelled: {subscription_id}')
                return True
            else:
                logger.error(f'Mercado Pago error: {result}')
                return False
        except Exception as e:
            logger.error(f'Mercado Pago error: {str(e)}')
            return False

    def verify_webhook(self, data):
        """Verify Mercado Pago webhook"""
        try:
            # Mercado Pago webhook verification
            # Implementar validação de assinatura se necessário
            logger.info(f'Mercado Pago webhook received: {data}')
            return True
        except Exception as e:
            logger.error(f'Mercado Pago webhook error: {str(e)}')
            return False

    def get_payment_methods(self):
        """Get available payment methods"""
        if not self.sdk:
            logger.error('Mercado Pago SDK not configured')
            return []

        try:
            result = self.sdk.payment_method().list_all()

            if result['status'] == 200:
                logger.info('Mercado Pago payment methods retrieved')
                return result['response']
            else:
                logger.error(f'Mercado Pago error: {result}')
                return []
        except Exception as e:
            logger.error(f'Mercado Pago error: {str(e)}')
            return []

    def create_plan(self, plan_data):
        """Create a subscription plan"""
        if not self.sdk:
            logger.error('Mercado Pago SDK not configured')
            return None

        try:
            result = self.sdk.plan().create(plan_data)

            if result['status'] == 201:
                logger.info(f'Mercado Pago plan created: {result["response"]["id"]}')
                return result['response']
            else:
                logger.error(f'Mercado Pago error: {result}')
                return None
        except Exception as e:
            logger.error(f'Mercado Pago error: {str(e)}')
            return None

