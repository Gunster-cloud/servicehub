from rest_framework import serializers
from .models import Quote, QuoteItem, Proposal


class QuoteItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuoteItem
        fields = ['id', 'description', 'quantity', 'unit_price', 'total', 'order']


class QuoteSerializer(serializers.ModelSerializer):
    items = QuoteItemSerializer(many=True, read_only=True)
    client_name = serializers.CharField(source='client.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = Quote
        fields = [
            'id', 'quote_number', 'client', 'client_name', 'title', 'description',
            'subtotal', 'discount', 'tax', 'total', 'status', 'valid_until',
            'sent_at', 'viewed_at', 'approved_at', 'created_by', 'created_by_name',
            'assigned_to', 'created_at', 'updated_at', 'items'
        ]
        read_only_fields = ['id', 'quote_number', 'created_at', 'updated_at', 'created_by']


class QuoteCreateSerializer(serializers.ModelSerializer):
    items = QuoteItemSerializer(many=True, write_only=True)
    
    class Meta:
        model = Quote
        fields = [
            'client', 'title', 'description', 'subtotal', 'discount', 'tax', 'total',
            'valid_until', 'assigned_to', 'items'
        ]
    
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        quote = Quote.objects.create(**validated_data)
        for item_data in items_data:
            QuoteItem.objects.create(quote=quote, **item_data)
        return quote


class ProposalSerializer(serializers.ModelSerializer):
    quote = QuoteSerializer(read_only=True)
    
    class Meta:
        model = Proposal
        fields = [
            'id', 'quote', 'proposal_number', 'status', 'terms',
            'payment_terms', 'warranty', 'sent_at', 'accepted_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'proposal_number', 'created_at', 'updated_at']

