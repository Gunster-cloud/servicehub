from django.contrib import admin
from .models import SalesMetrics, DailyActivity, Report


@admin.register(SalesMetrics)
class SalesMetricsAdmin(admin.ModelAdmin):
    list_display = ('user', 'period_start', 'period_end', 'total_revenue', 'conversion_rate')
    list_filter = ('period_start', 'period_end')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(DailyActivity)
class DailyActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'created_at')
    list_filter = ('activity_type', 'created_at')
    search_fields = ('user__username', 'description')
    readonly_fields = ('created_at',)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('name', 'report_type', 'period_start', 'period_end', 'created_at')
    list_filter = ('report_type', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at',)

