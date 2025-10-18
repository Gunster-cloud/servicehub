from rest_framework import serializers
from .models import Client, ClientContact
from servicehub.utils.validators import ClientValidator


class ClientContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientContact
        fields = ['id', 'name', 'email', 'phone', 'position', 'is_primary', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ClientSerializer(serializers.ModelSerializer):
    contacts = ClientContactSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    is_deleted = serializers.SerializerMethodField()
    
    class Meta:
        model = Client
        fields = [
            'id', 'name', 'email', 'phone', 'type', 'document',
            'address', 'city', 'state', 'zip_code', 'company_name',
            'contact_person', 'notes', 'status', 'created_by', 'created_by_name',
            'assigned_to', 'assigned_to_name', 'created_at', 'updated_at', 'last_contact',
            'contacts', 'is_deleted'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'is_deleted']
    
    def get_is_deleted(self, obj):
        return obj.is_deleted
    
    def validate(self, data):
        """Validate using Pydantic."""
        try:
            ClientValidator(
                name=data.get('name'),
                email=data.get('email'),
                phone=data.get('phone'),
                document=data.get('document'),
                type=data.get('type', 'individual')
            )
        except Exception as e:
            raise serializers.ValidationError(str(e))
        return data


class ClientCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = [
            'name', 'email', 'phone', 'type', 'document',
            'address', 'city', 'state', 'zip_code', 'company_name',
            'contact_person', 'notes', 'assigned_to'
        ]
    
    def validate(self, data):
        """Validate using Pydantic."""
        try:
            ClientValidator(
                name=data.get('name'),
                email=data.get('email'),
                phone=data.get('phone'),
                document=data.get('document'),
                type=data.get('type', 'individual')
            )
        except Exception as e:
            raise serializers.ValidationError(str(e))
        return data


class ClientListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    
    class Meta:
        model = Client
        fields = ['id', 'name', 'email', 'phone', 'type', 'status', 'created_at']
        read_only_fields = ['id', 'created_at']

