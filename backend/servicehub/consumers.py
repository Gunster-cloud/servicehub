"""
WebSocket Consumers for Real-time Notifications
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)


class NotificationConsumer(AsyncWebsocketConsumer):
    """Consumer for real-time notifications"""

    async def connect(self):
        """Handle WebSocket connection"""
        self.user = self.scope['user']
        self.user_id = self.user.id if self.user.is_authenticated else None
        
        if not self.user.is_authenticated:
            await self.close()
            return

        # Create user-specific group
        self.group_name = f'notifications_{self.user_id}'
        
        # Join group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
        logger.info(f'User {self.user_id} connected to notifications')

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if self.user_id:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
            logger.info(f'User {self.user_id} disconnected from notifications')

    async def receive(self, text_data):
        """Receive message from WebSocket"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': str(datetime.now())
                }))
        except json.JSONDecodeError:
            logger.error('Invalid JSON received')

    async def notification_message(self, event):
        """Send notification to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': event['type'],
            'title': event['title'],
            'message': event['message'],
            'data': event.get('data', {}),
            'timestamp': event.get('timestamp'),
        }))

    async def quote_update(self, event):
        """Send quote update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'quote_update',
            'quote_id': event['quote_id'],
            'status': event['status'],
            'message': event['message'],
            'timestamp': event.get('timestamp'),
        }))

    async def client_update(self, event):
        """Send client update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'client_update',
            'client_id': event['client_id'],
            'action': event['action'],
            'data': event.get('data', {}),
            'timestamp': event.get('timestamp'),
        }))


class QuoteConsumer(AsyncWebsocketConsumer):
    """Consumer for quote updates"""

    async def connect(self):
        """Handle WebSocket connection"""
        self.user = self.scope['user']
        
        if not self.user.is_authenticated:
            await self.close()
            return

        self.group_name = 'quotes_updates'
        
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
        logger.info(f'User {self.user.id} connected to quotes')

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def quote_created(self, event):
        """Send quote created message"""
        await self.send(text_data=json.dumps({
            'type': 'quote_created',
            'quote_id': event['quote_id'],
            'title': event['title'],
            'client': event['client'],
            'value': str(event['value']),
            'timestamp': event.get('timestamp'),
        }))

    async def quote_status_changed(self, event):
        """Send quote status change message"""
        await self.send(text_data=json.dumps({
            'type': 'quote_status_changed',
            'quote_id': event['quote_id'],
            'old_status': event['old_status'],
            'new_status': event['new_status'],
            'timestamp': event.get('timestamp'),
        }))


class ActivityConsumer(AsyncWebsocketConsumer):
    """Consumer for activity feed"""

    async def connect(self):
        """Handle WebSocket connection"""
        self.user = self.scope['user']
        
        if not self.user.is_authenticated:
            await self.close()
            return

        self.group_name = f'activity_{self.user.id}'
        
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def activity_log(self, event):
        """Send activity log message"""
        await self.send(text_data=json.dumps({
            'type': 'activity',
            'action': event['action'],
            'user': event['user'],
            'entity': event['entity'],
            'timestamp': event.get('timestamp'),
        }))

