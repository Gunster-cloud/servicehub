from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import SalesMetrics, DailyActivity, Report
from .serializers import SalesMetricsSerializer, DailyActivitySerializer, ReportSerializer


class SalesMetricsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Sales Metrics (Read-only).
    """
    
    queryset = SalesMetrics.objects.all()
    serializer_class = SalesMetricsSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['user', 'period_start', 'period_end']
    ordering_fields = ['period_end']
    ordering = ['-period_end']


class DailyActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Daily Activities (Read-only).
    """
    
    queryset = DailyActivity.objects.all()
    serializer_class = DailyActivitySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user', 'activity_type']
    search_fields = ['description']
    ordering_fields = ['created_at']
    ordering = ['-created_at']


class ReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Reports.
    """
    
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['report_type']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

