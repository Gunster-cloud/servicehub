"""
Payment Service - Stripe and PayPal Integration
"""

import stripe
from paypalrestsdk import Api, Payment
from django.conf import settings
from decouple import config
import logging

logger = logging.getLogger(__name__)

# Stripe Configuration
stripe.api_key = config('STRIPE_SECRET_KEY', default='')

# PayPal Configuration
paypal_api = Api({
    'mode': config('PAYPAL_MODE', default='sandbox'),
    'client_id': config('PAYPAL_CLIENT_ID', default=''),
    'client_secret': config('PAYPAL_CLIENT_SECRET', default=''),
})


class StripePaymentService:
    """Service for Stripe payments"""

    @staticmethod
    def create_payment_intent(amount, currency='brl', description='', metadata=None):
        """Create a Stripe payment intent"""
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency=currency,
                description=description,
                metadata=metadata or {},
            )
            logger.info(f'Payment intent created: {intent.id}')
            return intent
        except stripe.error.StripeError as e:
            logger.error(f'Stripe error: {str(e)}')
            return None

    @staticmethod
    def confirm_payment(payment_intent_id):
        """Confirm a payment intent"""
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return intent.status == 'succeeded'
        except stripe.error.StripeError as e:
            logger.error(f'Stripe error: {str(e)}')
            return False

    @staticmethod
    def create_customer(email, name=None, metadata=None):
        """Create a Stripe customer"""
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata=metadata or {},
            )
            logger.info(f'Customer created: {customer.id}')
            return customer
        except stripe.error.StripeError as e:
            logger.error(f'Stripe error: {str(e)}')
            return None

    @staticmethod
    def create_invoice(customer_id, amount, description='', metadata=None):
        """Create a Stripe invoice"""
        try:
            invoice = stripe.Invoice.create(
                customer=customer_id,
                description=description,
                metadata=metadata or {},
            )
            
            # Add line item
            stripe.InvoiceItem.create(
                customer=customer_id,
                amount=int(amount * 100),
                currency='brl',
                description=description,
                invoice=invoice.id,
            )
            
            # Finalize and send
            invoice.finalize_invoice()
            invoice.send_invoice()
            
            logger.info(f'Invoice created: {invoice.id}')
            return invoice
        except stripe.error.StripeError as e:
            logger.error(f'Stripe error: {str(e)}')
            return None

    @staticmethod
    def refund_payment(payment_intent_id, amount=None):
        """Refund a payment"""
        try:
            refund = stripe.Refund.create(
                payment_intent=payment_intent_id,
                amount=int(amount * 100) if amount else None,
            )
            logger.info(f'Refund created: {refund.id}')
            return refund
        except stripe.error.StripeError as e:
            logger.error(f'Stripe error: {str(e)}')
            return None


class PayPalPaymentService:
    """Service for PayPal payments"""

    @staticmethod
    def create_payment(amount, description='', return_url='', cancel_url=''):
        """Create a PayPal payment"""
        try:
            payment = Payment({
                'intent': 'sale',
                'payer': {
                    'payment_method': 'paypal'
                },
                'redirect_urls': {
                    'return_url': return_url,
                    'cancel_url': cancel_url,
                },
                'transactions': [{
                    'amount': {
                        'total': str(amount),
                        'currency': 'BRL',
                        'details': {
                            'subtotal': str(amount),
                        }
                    },
                    'description': description,
                }]
            })

            if payment.create():
                logger.info(f'PayPal payment created: {payment.id}')
                return payment
            else:
                logger.error(f'PayPal error: {payment.error}')
                return None
        except Exception as e:
            logger.error(f'PayPal error: {str(e)}')
            return None

    @staticmethod
    def execute_payment(payment_id, payer_id):
        """Execute a PayPal payment"""
        try:
            payment = Payment.find(payment_id)
            
            if payment.execute({'payer_id': payer_id}):
                logger.info(f'PayPal payment executed: {payment.id}')
                return payment
            else:
                logger.error(f'PayPal error: {payment.error}')
                return None
        except Exception as e:
            logger.error(f'PayPal error: {str(e)}')
            return None

    @staticmethod
    def refund_payment(sale_id, amount=None):
        """Refund a PayPal payment"""
        try:
            from paypalrestsdk import Sale
            
            sale = Sale.find(sale_id)
            
            refund_dict = {}
            if amount:
                refund_dict['amount'] = {
                    'currency': 'BRL',
                    'total': str(amount),
                }
            
            if sale.refund(refund_dict):
                logger.info(f'PayPal refund created: {sale.id}')
                return sale
            else:
                logger.error(f'PayPal error: {sale.error}')
                return None
        except Exception as e:
            logger.error(f'PayPal error: {str(e)}')
            return None


class PaymentService:
    """Unified payment service"""

    @staticmethod
    def create_payment(amount, method='stripe', **kwargs):
        """Create payment using preferred method"""
        if method == 'stripe':
            return StripePaymentService.create_payment_intent(amount, **kwargs)
        elif method == 'paypal':
            return PayPalPaymentService.create_payment(amount, **kwargs)
        else:
            logger.error(f'Unknown payment method: {method}')
            return None

    @staticmethod
    def confirm_payment(payment_id, method='stripe'):
        """Confirm payment"""
        if method == 'stripe':
            return StripePaymentService.confirm_payment(payment_id)
        elif method == 'paypal':
            return PayPalPaymentService.execute_payment(payment_id, None)
        else:
            logger.error(f'Unknown payment method: {method}')
            return False

    @staticmethod
    def refund_payment(payment_id, method='stripe', amount=None):
        """Refund payment"""
        if method == 'stripe':
            return StripePaymentService.refund_payment(payment_id, amount)
        elif method == 'paypal':
            return PayPalPaymentService.refund_payment(payment_id, amount)
        else:
            logger.error(f'Unknown payment method: {method}')
            return None

