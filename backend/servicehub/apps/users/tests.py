"""
Tests for Users app.
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    """Tests for User model."""
    
    def test_create_user(self):
        """Test creating a user."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.get_full_name() == 'Test User'
    
    def test_create_superuser(self):
        """Test creating a superuser."""
        user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        assert user.is_superuser
        assert user.is_staff
    
    def test_user_role_choices(self):
        """Test user role choices."""
        user = User.objects.create_user(
            username='salesperson',
            email='sales@example.com',
            password='testpass123',
            role='salesperson'
        )
        assert user.role == 'salesperson'


@pytest.mark.django_db
class TestUserAPI:
    """Tests for User API."""
    
    def setup_method(self):
        """Setup test client and users."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_register_user(self):
        """Test user registration."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post('/api/v1/users/register/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['username'] == 'newuser'
    
    def test_get_current_user(self):
        """Test getting current user."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/users/me/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == 'testuser'
    
    def test_list_users(self):
        """Test listing users."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/users/')
        assert response.status_code == status.HTTP_200_OK
    
    def test_change_password(self):
        """Test changing password."""
        self.client.force_authenticate(user=self.user)
        data = {
            'old_password': 'testpass123',
            'new_password': 'newpass456',
            'new_password_confirm': 'newpass456'
        }
        response = self.client.post(f'/api/v1/users/{self.user.id}/change-password/', data)
        assert response.status_code == status.HTTP_200_OK

