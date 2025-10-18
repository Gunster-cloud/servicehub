"""
Tests for Quotes app.
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from servicehub.apps.clients.models import Client
from .models import Quote, QuoteItem, Proposal

User = get_user_model()


@pytest.mark.django_db
class TestQuoteModel:
    """Tests for Quote model."""
    
    def setup_method(self):
        """Setup test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client_obj = Client.objects.create(
            name='Test Client',
            email='client@example.com',
            phone='11999999999',
            type='individual',
            document='12345678901',
            created_by=self.user
        )
    
    def test_create_quote(self):
        """Test creating a quote."""
        quote = Quote.objects.create(
            client=self.client_obj,
            title='Test Quote',
            description='Test Description',
            subtotal=1000.00,
            discount=100.00,
            tax=180.00,
            total=1080.00,
            created_by=self.user
        )
        assert quote.title == 'Test Quote'
        assert quote.total == 1080.00
        assert quote.quote_number  # Should be auto-generated
    
    def test_quote_number_auto_generation(self):
        """Test quote number auto-generation."""
        quote = Quote.objects.create(
            client=self.client_obj,
            title='Test Quote',
            description='Test Description',
            subtotal=1000.00,
            discount=0,
            tax=0,
            total=1000.00,
            created_by=self.user
        )
        assert quote.quote_number.startswith('QT-')
    
    def test_add_quote_items(self):
        """Test adding items to a quote."""
        quote = Quote.objects.create(
            client=self.client_obj,
            title='Test Quote',
            description='Test Description',
            subtotal=1000.00,
            discount=0,
            tax=0,
            total=1000.00,
            created_by=self.user
        )
        item = QuoteItem.objects.create(
            quote=quote,
            description='Service 1',
            quantity=10,
            unit_price=100.00,
            total=1000.00,
            order=1
        )
        assert item in quote.items.all()
    
    def test_soft_delete_quote(self):
        """Test soft deleting a quote."""
        quote = Quote.objects.create(
            client=self.client_obj,
            title='Test Quote',
            description='Test Description',
            subtotal=1000.00,
            discount=0,
            tax=0,
            total=1000.00,
            created_by=self.user
        )
        quote.delete()
        
        assert quote.is_deleted
        assert Quote.objects.filter(id=quote.id).count() == 0


@pytest.mark.django_db
class TestQuoteAPI:
    """Tests for Quote API."""
    
    def setup_method(self):
        """Setup test client and data."""
        self.api_client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client_obj = Client.objects.create(
            name='Test Client',
            email='client@example.com',
            phone='11999999999',
            type='individual',
            document='12345678901',
            created_by=self.user
        )
    
    def test_create_quote(self):
        """Test creating a quote via API."""
        self.api_client.force_authenticate(user=self.user)
        data = {
            'client': self.client_obj.id,
            'title': 'Test Quote',
            'description': 'Test Description',
            'subtotal': 1000.00,
            'discount': 100.00,
            'tax': 180.00,
            'total': 1080.00,
            'items': [
                {
                    'description': 'Service 1',
                    'quantity': 10,
                    'unit_price': 100.00,
                    'total': 1000.00,
                    'order': 1
                }
            ]
        }
        response = self.api_client.post('/api/v1/quotes/quotes/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'Test Quote'
    
    def test_send_quote(self):
        """Test sending a quote."""
        self.api_client.force_authenticate(user=self.user)
        quote = Quote.objects.create(
            client=self.client_obj,
            title='Test Quote',
            description='Test Description',
            subtotal=1000.00,
            discount=0,
            tax=0,
            total=1000.00,
            created_by=self.user
        )
        response = self.api_client.post(f'/api/v1/quotes/quotes/{quote.id}/send/')
        assert response.status_code == status.HTTP_200_OK
        
        quote.refresh_from_db()
        assert quote.status == 'sent'
        assert quote.sent_at is not None
    
    def test_approve_quote(self):
        """Test approving a quote."""
        self.api_client.force_authenticate(user=self.user)
        quote = Quote.objects.create(
            client=self.client_obj,
            title='Test Quote',
            description='Test Description',
            subtotal=1000.00,
            discount=0,
            tax=0,
            total=1000.00,
            status='sent',
            created_by=self.user
        )
        response = self.api_client.post(f'/api/v1/quotes/quotes/{quote.id}/approve/')
        assert response.status_code == status.HTTP_200_OK
        
        quote.refresh_from_db()
        assert quote.status == 'approved'

