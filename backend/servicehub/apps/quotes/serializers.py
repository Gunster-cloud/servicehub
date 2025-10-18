from rest_framework import serializers
from .models import Quote, QuoteItem, Proposal
from servicehub.utils.validators import QuoteValidator


class QuoteItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuoteItem
        fields = ['id', 'description', 'quantity', 'unit_price', 'total', 'order', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class QuoteSerializer(serializers.ModelSerializer):
    items = QuoteItemSerializer(many=True, read_only=True)
    client_name = serializers.CharField(source='client.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    is_deleted = serializers.SerializerMethodField()
    
    class Meta:
        model = Quote
        fields = [
            'id', 'quote_number', 'client', 'client_name', 'title', 'description',
            'subtotal', 'discount', 'tax', 'total', 'status', 'valid_until',
            'sent_at', 'viewed_at', 'approved_at', 'created_by', 'created_by_name',
            'assigned_to', 'created_at', 'updated_at', 'items', 'is_deleted'
        ]
        read_only_fields = ['id', 'quote_number', 'created_at', 'updated_at', 'created_by', 'is_deleted']
    
    def get_is_deleted(self, obj):
        return obj.is_deleted
    
    def validate(self, data):
        """Validate using Pydantic."""
        try:
            QuoteValidator(
                title=data.get('title'),
                subtotal=data.get('subtotal'),
                discount=data.get('discount', 0),
                tax=data.get('tax', 0),
                total=data.get('total')
            )
        except Exception as e:
            raise serializers.ValidationError(str(e))
        return data


class QuoteCreateSerializer(serializers.ModelSerializer):
    items = QuoteItemSerializer(many=True, write_only=True, required=False)
    
    class Meta:
        model = Quote
        fields = [
            'client', 'title', 'description', 'subtotal', 'discount', 'tax', 'total',
            'valid_until', 'assigned_to', 'items'
        ]
    
    def validate(self, data):
        """Validate using Pydantic."""
        try:
            QuoteValidator(
                title=data.get('title'),
                subtotal=data.get('subtotal'),
                discount=data.get('discount', 0),
                tax=data.get('tax', 0),
                total=data.get('total')
            )
        except Exception as e:
            raise serializers.ValidationError(str(e))
        return data
    
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        quote = Quote.objects.create(**validated_data)
        for item_data in items_data:
            QuoteItem.objects.create(quote=quote, **item_data)
        return quote


class QuoteListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    
    class Meta:
        model = Quote
        fields = ['id', 'quote_number', 'client', 'title', 'total', 'status', 'created_at']
        read_only_fields = ['id', 'created_at']


class ProposalSerializer(serializers.ModelSerializer):
    quote = QuoteSerializer(read_only=True)
    is_deleted = serializers.SerializerMethodField()
    
    class Meta:
        model = Proposal
        fields = [
            'id', 'quote', 'proposal_number', 'status', 'terms',
            'payment_terms', 'warranty', 'sent_at', 'accepted_at',
            'created_at', 'updated_at', 'is_deleted'
        ]
        read_only_fields = ['id', 'proposal_number', 'created_at', 'updated_at', 'is_deleted']
    
    def get_is_deleted(self, obj):
        return obj.is_deleted


class ProposalCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proposal
        fields = ['quote', 'terms', 'payment_terms', 'warranty']

