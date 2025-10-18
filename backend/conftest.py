"""
Pytest configuration for ServiceHub.
"""

import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )


@pytest.fixture
def admin_user():
    """Create a test admin user."""
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpass123'
    )


@pytest.fixture
def salesperson_user():
    """Create a test salesperson user."""
    return User.objects.create_user(
        username='salesperson',
        email='sales@example.com',
        password='salespass123',
        role='salesperson'
    )

