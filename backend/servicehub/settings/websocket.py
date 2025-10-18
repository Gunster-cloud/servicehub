"""
WebSocket Configuration for Real-time Notifications
"""

from decouple import config

# Django Channels Configuration
INSTALLED_APPS = [
    'daphne',  # ASGI server
    'channels',
    'channels_redis',
]

# Channels Configuration
ASGI_APPLICATION = 'config.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('redis', 6379)],
            'password': config('REDIS_PASSWORD', default='changeme'),
            'capacity': 1500,
            'expiry': 10,
        },
    },
}

# WebSocket settings
WEBSOCKET_ACCEPT_ALL = False
WEBSOCKET_URL_PATTERN = r'^ws/'

# Notification settings
NOTIFICATION_TYPES = {
    'quote_created': 'Novo Orçamento',
    'quote_updated': 'Orçamento Atualizado',
    'quote_approved': 'Orçamento Aprovado',
    'quote_rejected': 'Orçamento Rejeitado',
    'client_added': 'Novo Cliente',
    'service_completed': 'Serviço Concluído',
    'payment_received': 'Pagamento Recebido',
}

# Real-time update channels
NOTIFICATION_CHANNELS = {
    'notifications': 'notifications',
    'quotes': 'quotes',
    'clients': 'clients',
    'services': 'services',
    'payments': 'payments',
}

