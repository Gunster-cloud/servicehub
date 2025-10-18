from django.contrib import admin
from .models import Service, ServiceCategory, ServiceOrder


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'base_price', 'unit', 'status')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ServiceOrder)
class ServiceOrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'service', 'status', 'scheduled_date')
    list_filter = ('status', 'scheduled_date', 'created_at')
    search_fields = ('order_number', 'service__name')
    readonly_fields = ('order_number', 'created_at', 'updated_at')

