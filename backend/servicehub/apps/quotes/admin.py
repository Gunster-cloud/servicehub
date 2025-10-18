from django.contrib import admin
from .models import Quote, QuoteItem, Proposal


class QuoteItemInline(admin.TabularInline):
    model = QuoteItem
    extra = 1


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ('quote_number', 'client', 'status', 'total', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('quote_number', 'client__name', 'title')
    readonly_fields = ('quote_number', 'created_at', 'updated_at')
    inlines = [QuoteItemInline]


@admin.register(QuoteItem)
class QuoteItemAdmin(admin.ModelAdmin):
    list_display = ('description', 'quote', 'quantity', 'unit_price', 'total')
    list_filter = ('quote',)
    search_fields = ('description', 'quote__quote_number')


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = ('proposal_number', 'quote', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('proposal_number', 'quote__quote_number')
    readonly_fields = ('proposal_number', 'created_at', 'updated_at')

