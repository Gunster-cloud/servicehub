"""
Custom filters for ServiceHub.
"""

from django_filters import rest_framework as filters
from servicehub.apps.clients.models import Client
from servicehub.apps.quotes.models import Quote
from servicehub.apps.services.models import Service, ServiceOrder


class ClientFilter(filters.FilterSet):
    """Advanced filters for Client."""
    
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    email = filters.CharFilter(field_name='email', lookup_expr='icontains')
    phone = filters.CharFilter(field_name='phone', lookup_expr='icontains')
    document = filters.CharFilter(field_name='document', lookup_expr='exact')
    city = filters.CharFilter(field_name='city', lookup_expr='icontains')
    state = filters.CharFilter(field_name='state', lookup_expr='exact')
    status = filters.ChoiceFilter(
        field_name='status',
        choices=[('active', 'Ativo'), ('inactive', 'Inativo'), ('blocked', 'Bloqueado')]
    )
    type = filters.ChoiceFilter(
        field_name='type',
        choices=[('individual', 'Pessoa Física'), ('company', 'Pessoa Jurídica')]
    )
    created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = Client
        fields = ['name', 'email', 'phone', 'document', 'city', 'state', 'status', 'type']


class QuoteFilter(filters.FilterSet):
    """Advanced filters for Quote."""
    
    quote_number = filters.CharFilter(field_name='quote_number', lookup_expr='icontains')
    title = filters.CharFilter(field_name='title', lookup_expr='icontains')
    client_name = filters.CharFilter(field_name='client__name', lookup_expr='icontains')
    status = filters.ChoiceFilter(
        field_name='status',
        choices=[
            ('draft', 'Rascunho'),
            ('sent', 'Enviado'),
            ('viewed', 'Visualizado'),
            ('approved', 'Aprovado'),
            ('rejected', 'Rejeitado'),
            ('expired', 'Expirado'),
        ]
    )
    total_min = filters.NumberFilter(field_name='total', lookup_expr='gte')
    total_max = filters.NumberFilter(field_name='total', lookup_expr='lte')
    created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    valid_until_after = filters.DateFilter(field_name='valid_until', lookup_expr='gte')
    valid_until_before = filters.DateFilter(field_name='valid_until', lookup_expr='lte')
    
    class Meta:
        model = Quote
        fields = ['quote_number', 'title', 'client', 'status', 'total_min', 'total_max']


class ServiceFilter(filters.FilterSet):
    """Advanced filters for Service."""
    
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    category = filters.CharFilter(field_name='category', lookup_expr='icontains')
    status = filters.ChoiceFilter(
        field_name='status',
        choices=[('active', 'Ativo'), ('inactive', 'Inativo'), ('archived', 'Arquivado')]
    )
    price_min = filters.NumberFilter(field_name='base_price', lookup_expr='gte')
    price_max = filters.NumberFilter(field_name='base_price', lookup_expr='lte')
    
    class Meta:
        model = Service
        fields = ['name', 'category', 'status', 'price_min', 'price_max']


class ServiceOrderFilter(filters.FilterSet):
    """Advanced filters for ServiceOrder."""
    
    order_number = filters.CharFilter(field_name='order_number', lookup_expr='icontains')
    service_name = filters.CharFilter(field_name='service__name', lookup_expr='icontains')
    status = filters.ChoiceFilter(
        field_name='status',
        choices=[
            ('pending', 'Pendente'),
            ('in_progress', 'Em Progresso'),
            ('completed', 'Concluído'),
            ('cancelled', 'Cancelado'),
        ]
    )
    scheduled_after = filters.DateTimeFilter(field_name='scheduled_date', lookup_expr='gte')
    scheduled_before = filters.DateTimeFilter(field_name='scheduled_date', lookup_expr='lte')
    
    class Meta:
        model = ServiceOrder
        fields = ['order_number', 'service', 'status', 'scheduled_after', 'scheduled_before']

