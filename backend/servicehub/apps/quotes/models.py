from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from servicehub.apps.clients.models import Client
from servicehub.utils.models import SoftDeleteModel, AuditModel

User = get_user_model()


class Quote(SoftDeleteModel, AuditModel):
    """
    Quote/Budget model for ServiceHub with soft delete and audit trail.
    """
    
    STATUS_CHOICES = (
        ('draft', _('Rascunho')),
        ('sent', _('Enviado')),
        ('viewed', _('Visualizado')),
        ('approved', _('Aprovado')),
        ('rejected', _('Rejeitado')),
        ('expired', _('Expirado')),
    )
    
    # Basic Information
    quote_number = models.CharField(_('número do orçamento'), max_length=50, unique=True, blank=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='quotes')
    title = models.CharField(_('título'), max_length=255)
    description = models.TextField(_('descrição'))
    
    # Financial Information
    subtotal = models.DecimalField(_('subtotal'), max_digits=10, decimal_places=2)
    discount = models.DecimalField(_('desconto'), max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(_('imposto'), max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(_('total'), max_digits=10, decimal_places=2)
    
    # Status and Dates
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='draft')
    valid_until = models.DateField(_('válido até'), null=True, blank=True)
    sent_at = models.DateTimeField(_('enviado em'), null=True, blank=True)
    viewed_at = models.DateTimeField(_('visualizado em'), null=True, blank=True)
    approved_at = models.DateTimeField(_('aprovado em'), null=True, blank=True)
    
    # Relationships
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='quotes_created')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='quotes_assigned')
    
    class Meta:
        verbose_name = _('Orçamento')
        verbose_name_plural = _('Orçamentos')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['quote_number']),
            models.Index(fields=['status']),
            models.Index(fields=['client']),
            models.Index(fields=['deleted_at']),
        ]

    def __str__(self):
        return f"{self.quote_number} - {self.client.name}"


class QuoteItem(AuditModel):
    """
    Line items for a quote.
    """
    
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(_('descrição'), max_length=255)
    quantity = models.DecimalField(_('quantidade'), max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(_('preço unitário'), max_digits=10, decimal_places=2)
    total = models.DecimalField(_('total'), max_digits=10, decimal_places=2)
    order = models.PositiveIntegerField(_('ordem'), default=0)
    
    class Meta:
        verbose_name = _('Item do Orçamento')
        verbose_name_plural = _('Itens do Orçamento')
        ordering = ['order']
    
    def __str__(self):
        return f"{self.description} - {self.quote.quote_number}"


class Proposal(SoftDeleteModel, AuditModel):
    """
    Proposal model (evolved from Quote) with soft delete and audit trail.
    """
    
    STATUS_CHOICES = (
        ('draft', _('Rascunho')),
        ('sent', _('Enviado')),
        ('viewed', _('Visualizado')),
        ('accepted', _('Aceito')),
        ('rejected', _('Rejeitado')),
        ('expired', _('Expirado')),
    )
    
    quote = models.OneToOneField(Quote, on_delete=models.CASCADE, related_name='proposal')
    proposal_number = models.CharField(_('número da proposta'), max_length=50, unique=True, blank=True)
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Terms and Conditions
    terms = models.TextField(_('termos e condições'), blank=True)
    payment_terms = models.CharField(_('condições de pagamento'), max_length=255, blank=True)
    warranty = models.CharField(_('garantia'), max_length=255, blank=True)
    
    # Dates
    sent_at = models.DateTimeField(_('enviado em'), null=True, blank=True)
    accepted_at = models.DateTimeField(_('aceito em'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('Proposta')
        verbose_name_plural = _('Propostas')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['proposal_number']),
            models.Index(fields=['status']),
            models.Index(fields=['deleted_at']),
        ]
    
    def __str__(self):
        return f"{self.proposal_number} - {self.quote.client.name}"

