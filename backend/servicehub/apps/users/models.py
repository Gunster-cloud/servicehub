from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom User model for ServiceHub.
    """
    
    ROLE_CHOICES = (
        ('admin', _('Administrador')),
        ('manager', _('Gerenciador')),
        ('salesperson', _('Vendedor')),
        ('technician', _('Técnico')),
        ('client', _('Cliente')),
    )
    
    email = models.EmailField(_('email address'), unique=True)
    phone = models.CharField(_('telefone'), max_length=20, blank=True)
    role = models.CharField(_('função'), max_length=20, choices=ROLE_CHOICES, default='salesperson')
    company_name = models.CharField(_('nome da empresa'), max_length=255, blank=True)
    document = models.CharField(_('CPF/CNPJ'), max_length=20, blank=True, null=True)
    is_active = models.BooleanField(_('ativo'), default=True)
    created_at = models.DateTimeField(_('criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('atualizado em'), auto_now=True)
    
    class Meta:
        verbose_name = _('Usuário')
        verbose_name_plural = _('Usuários')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def get_full_name(self):
        """Return the user's full name."""
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name or self.username


class UserProfile(models.Model):
    """
    Extended user profile for additional information.
    """
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(_('biografia'), blank=True)
    avatar = models.ImageField(_('avatar'), upload_to='avatars/', null=True, blank=True)
    address = models.CharField(_('endereço'), max_length=255, blank=True)
    city = models.CharField(_('cidade'), max_length=100, blank=True)
    state = models.CharField(_('estado'), max_length=2, blank=True)
    zip_code = models.CharField(_('CEP'), max_length=10, blank=True)
    preferences = models.JSONField(_('preferências'), default=dict, blank=True)
    created_at = models.DateTimeField(_('criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('atualizado em'), auto_now=True)
    
    class Meta:
        verbose_name = _('Perfil do Usuário')
        verbose_name_plural = _('Perfis dos Usuários')
    
    def __str__(self):
        return f"Perfil de {self.user.get_full_name()}"

