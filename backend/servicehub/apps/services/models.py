from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Service(models.Model):
    """
    Service model for ServiceHub.
    """
    
    STATUS_CHOICES = (
        ('active', _('Ativo')),
        ('inactive', _('Inativo')),
        ('archived', _('Arquivado')),
    )
    
    name = models.CharField(_('nome'), max_length=255, unique=True)
    description = models.TextField(_('descrição'))
    category = models.CharField(_('categoria'), max_length=100, blank=True)
    base_price = models.DecimalField(_('preço base'), max_digits=10, decimal_places=2)
    unit = models.CharField(_('unidade'), max_length=50, default='hora')
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Additional Information
    notes = models.TextField(_('notas'), blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('atualizado em'), auto_now=True)
    
    class Meta:
        verbose_name = _('Serviço')
        verbose_name_plural = _('Serviços')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class ServiceCategory(models.Model):
    """
    Service categories for organization.
    """
    
    name = models.CharField(_('nome'), max_length=100, unique=True)
    description = models.TextField(_('descrição'), blank=True)
    icon = models.CharField(_('ícone'), max_length=50, blank=True)
    created_at = models.DateTimeField(_('criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('atualizado em'), auto_now=True)
    
    class Meta:
        verbose_name = _('Categoria de Serviço')
        verbose_name_plural = _('Categorias de Serviço')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class ServiceOrder(models.Model):
    """
    Service order model.
    """
    
    STATUS_CHOICES = (
        ('pending', _('Pendente')),
        ('in_progress', _('Em Progresso')),
        ('completed', _('Concluído')),
        ('cancelled', _('Cancelado')),
    )
    
    order_number = models.CharField(_('número do pedido'), max_length=50, unique=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='orders')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='service_orders')
    
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='pending')
    scheduled_date = models.DateTimeField(_('data agendada'))
    completed_date = models.DateTimeField(_('data de conclusão'), null=True, blank=True)
    
    notes = models.TextField(_('notas'), blank=True)
    
    created_at = models.DateTimeField(_('criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('atualizado em'), auto_now=True)
    
    class Meta:
        verbose_name = _('Pedido de Serviço')
        verbose_name_plural = _('Pedidos de Serviço')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.order_number} - {self.service.name}"

