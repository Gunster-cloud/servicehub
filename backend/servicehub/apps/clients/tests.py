"""
Tests for Clients app.
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import Client, ClientContact

User = get_user_model()


@pytest.mark.django_db
class TestClientModel:
    """Tests for Client model."""
    
    def setup_method(self):
        """Setup test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_client(self):
        """Test creating a client."""
        client = Client.objects.create(
            name='John Doe',
            email='john@example.com',
            phone='11999999999',
            type='individual',
            document='12345678901',
            created_by=self.user
        )
        assert client.name == 'John Doe'
        assert client.type == 'individual'
        assert not client.is_deleted
    
    def test_soft_delete_client(self):
        """Test soft deleting a client."""
        client = Client.objects.create(
            name='Jane Doe',
            email='jane@example.com',
            phone='11988888888',
            type='company',
            document='12345678901234',
            created_by=self.user
        )
        client.delete()
        
        assert client.is_deleted
        assert Client.objects.filter(id=client.id).count() == 0
        assert Client.all_objects.filter(id=client.id).count() == 1
    
    def test_restore_client(self):
        """Test restoring a deleted client."""
        client = Client.objects.create(
            name='Test Client',
            email='test@client.com',
            phone='11977777777',
            type='individual',
            document='98765432101',
            created_by=self.user
        )
        client.delete()
        client.restore()
        
        assert not client.is_deleted
        assert Client.objects.filter(id=client.id).count() == 1
    
    def test_add_contact(self):
        """Test adding a contact to a client."""
        client = Client.objects.create(
            name='Test Client',
            email='test@client.com',
            phone='11977777777',
            type='individual',
            document='98765432101',
            created_by=self.user
        )
        contact = ClientContact.objects.create(
            client=client,
            name='John Contact',
            email='john@contact.com',
            phone='11966666666',
            is_primary=True
        )
        assert contact in client.contacts.all()


@pytest.mark.django_db
class TestClientAPI:
    """Tests for Client API."""
    
    def setup_method(self):
        """Setup test client and users."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_client(self):
        """Test creating a client via API."""
        self.client.force_authenticate(user=self.user)
        data = {
            'name': 'Test Client',
            'email': 'test@client.com',
            'phone': '11999999999',
            'type': 'individual',
            'document': '12345678901'
        }
        response = self.client.post('/api/v1/clients/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'Test Client'
    
    def test_list_clients(self):
        """Test listing clients."""
        self.client.force_authenticate(user=self.user)
        Client.objects.create(
            name='Test Client',
            email='test@client.com',
            phone='11999999999',
            type='individual',
            document='12345678901',
            created_by=self.user
        )
        response = self.client.get('/api/v1/clients/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
    
    def test_filter_clients_by_status(self):
        """Test filtering clients by status."""
        self.client.force_authenticate(user=self.user)
        Client.objects.create(
            name='Active Client',
            email='active@client.com',
            phone='11999999999',
            type='individual',
            document='12345678901',
            status='active',
            created_by=self.user
        )
        Client.objects.create(
            name='Inactive Client',
            email='inactive@client.com',
            phone='11988888888',
            type='individual',
            document='98765432101',
            status='inactive',
            created_by=self.user
        )
        response = self.client.get('/api/v1/clients/?status=active')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

