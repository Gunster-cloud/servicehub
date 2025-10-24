from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from servicehub.utils.models import SoftDeleteModel, AuditModel

User = get_user_model()


class Client(SoftDeleteModel, AuditModel):
    """
    Client model for ServiceHub with soft delete and audit trail.
    """
    
    TYPE_CHOICES = (
        ('individual', _('Pessoa Física')),
        ('company', _('Pessoa Jurídica')),
    )
    
    STATUS_CHOICES = (
        ('active', _('Ativo')),
        ('inactive', _('Inativo')),
        ('blocked', _('Bloqueado')),
    )
    
    # Basic Information
    name = models.CharField(_('nome'), max_length=255)
    email = models.EmailField(_('email'), unique=True)
    phone = models.CharField(_('telefone'), max_length=20)
    type = models.CharField(_('tipo'), max_length=20, choices=TYPE_CHOICES, default='individual')
    document = models.CharField(_('CPF/CNPJ'), max_length=20, unique=True)
    
    # Address
    address = models.CharField(_('endereço'), max_length=255, blank=True)
    city = models.CharField(_('cidade'), max_length=100, blank=True)
    state = models.CharField(_('estado'), max_length=2, blank=True)
    zip_code = models.CharField(_('CEP'), max_length=10, blank=True)
    
    # Additional Information
    company_name = models.CharField(_('nome da empresa'), max_length=255, blank=True)
    contact_person = models.CharField(_('pessoa de contato'), max_length=255, blank=True)
    notes = models.TextField(_('notas'), blank=True)
    
    # Status
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Relationships
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='clients_created')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_clients')
    
    # Timestamps
    last_contact = models.DateTimeField(_('último contato'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('Cliente')
        verbose_name_plural = _('Clientes')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['document']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.email})"


class ClientContact(AuditModel):
    """
    Additional contacts for a client.
    """
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='contacts')
    name = models.CharField(_('nome'), max_length=255)
    email = models.EmailField(_('email'), blank=True)
    phone = models.CharField(_('telefone'), max_length=20, blank=True)
    position = models.CharField(_('cargo'), max_length=100, blank=True)
    is_primary = models.BooleanField(_('contato principal'), default=False)
    
    class Meta:
        verbose_name = _('Contato do Cliente')
        verbose_name_plural = _('Contatos dos Clientes')
    
    def __str__(self):
        return f"{self.name} - {self.client.name}"

