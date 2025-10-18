from django.contrib import admin
from .models import Client, ClientContact


class ClientContactInline(admin.TabularInline):
    model = ClientContact
    extra = 1


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'type', 'status', 'created_at')
    list_filter = ('status', 'type', 'created_at')
    search_fields = ('name', 'email', 'document', 'company_name')
    readonly_fields = ('created_at', 'updated_at', 'last_contact')
    inlines = [ClientContactInline]
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'email', 'phone', 'type', 'document')
        }),
        ('Endereço', {
            'fields': ('address', 'city', 'state', 'zip_code')
        }),
        ('Informações Adicionais', {
            'fields': ('company_name', 'contact_person', 'notes', 'status')
        }),
        ('Relacionamentos', {
            'fields': ('created_by', 'assigned_to')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_contact'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ClientContact)
class ClientContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'client', 'email', 'phone', 'is_primary')
    list_filter = ('is_primary', 'client')
    search_fields = ('name', 'email', 'client__name')

