from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from servicehub.apps.quotes.models import Quote

User = get_user_model()


class SalesMetrics(models.Model):
    """
    Sales metrics and KPIs.
    """
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales_metrics')
    
    # Metrics
    total_quotes = models.IntegerField(_('total de orçamentos'), default=0)
    approved_quotes = models.IntegerField(_('orçamentos aprovados'), default=0)
    rejected_quotes = models.IntegerField(_('orçamentos rejeitados'), default=0)
    total_revenue = models.DecimalField(_('receita total'), max_digits=15, decimal_places=2, default=0)
    average_quote_value = models.DecimalField(_('valor médio do orçamento'), max_digits=10, decimal_places=2, default=0)
    conversion_rate = models.DecimalField(_('taxa de conversão'), max_digits=5, decimal_places=2, default=0)
    
    # Period
    period_start = models.DateField(_('início do período'))
    period_end = models.DateField(_('fim do período'))
    
    # Timestamps
    created_at = models.DateTimeField(_('criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('atualizado em'), auto_now=True)
    
    class Meta:
        verbose_name = _('Métrica de Vendas')
        verbose_name_plural = _('Métricas de Vendas')
        ordering = ['-period_end']
    
    def __str__(self):
        return f"Métricas de {self.user.get_full_name()} ({self.period_start} - {self.period_end})"


class DailyActivity(models.Model):
    """
    Daily activity log for analytics.
    """
    
    ACTIVITY_TYPES = (
        ('quote_created', _('Orçamento Criado')),
        ('quote_sent', _('Orçamento Enviado')),
        ('quote_approved', _('Orçamento Aprovado')),
        ('client_added', _('Cliente Adicionado')),
        ('proposal_sent', _('Proposta Enviada')),
        ('service_completed', _('Serviço Concluído')),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_activities')
    activity_type = models.CharField(_('tipo de atividade'), max_length=50, choices=ACTIVITY_TYPES)
    description = models.TextField(_('descrição'))
    
    # Related objects
    quote = models.ForeignKey(Quote, on_delete=models.SET_NULL, null=True, blank=True, related_name='activities')
    
    # Metadata
    metadata = models.JSONField(_('metadados'), default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('criado em'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Atividade Diária')
        verbose_name_plural = _('Atividades Diárias')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['activity_type']),
        ]
    
    def __str__(self):
        return f"{self.get_activity_type_display()} - {self.user.get_full_name()}"


class Report(models.Model):
    """
    Generated reports.
    """
    
    REPORT_TYPES = (
        ('sales', _('Vendas')),
        ('revenue', _('Receita')),
        ('clients', _('Clientes')),
        ('performance', _('Desempenho')),
    )
    
    name = models.CharField(_('nome'), max_length=255)
    report_type = models.CharField(_('tipo de relatório'), max_length=50, choices=REPORT_TYPES)
    description = models.TextField(_('descrição'), blank=True)
    
    # Data
    data = models.JSONField(_('dados'))
    
    # Period
    period_start = models.DateField(_('início do período'))
    period_end = models.DateField(_('fim do período'))
    
    # Timestamps
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reports_created')
    created_at = models.DateTimeField(_('criado em'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Relatório')
        verbose_name_plural = _('Relatórios')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.period_start} - {self.period_end})"

