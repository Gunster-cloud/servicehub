from rest_framework import serializers
from .models import SalesMetrics, DailyActivity, Report


class SalesMetricsSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = SalesMetrics
        fields = [
            'id', 'user', 'user_name', 'total_quotes', 'approved_quotes',
            'rejected_quotes', 'total_revenue', 'average_quote_value',
            'conversion_rate', 'period_start', 'period_end', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DailyActivitySerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = DailyActivity
        fields = [
            'id', 'user', 'user_name', 'activity_type', 'description',
            'quote', 'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ReportSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = Report
        fields = [
            'id', 'name', 'report_type', 'description', 'data',
            'period_start', 'period_end', 'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

