from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Service, ServiceCategory, ServiceOrder
from .serializers import ServiceSerializer, ServiceCategorySerializer, ServiceOrderSerializer


class ServiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Service management.
    """
    
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'category']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'base_price']
    ordering = ['name']


class ServiceCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Service Categories.
    """
    
    queryset = ServiceCategory.objects.all()
    serializer_class = ServiceCategorySerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['name']
    ordering_fields = ['name']
    ordering = ['name']


class ServiceOrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Service Orders.
    """
    
    queryset = ServiceOrder.objects.all()
    serializer_class = ServiceOrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'service']
    search_fields = ['order_number', 'service__name']
    ordering_fields = ['created_at', 'scheduled_date']
    ordering = ['-created_at']

