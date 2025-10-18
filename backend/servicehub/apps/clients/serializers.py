from rest_framework import serializers
from .models import Client, ClientContact


class ClientContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientContact
        fields = ['id', 'name', 'email', 'phone', 'position', 'is_primary']


class ClientSerializer(serializers.ModelSerializer):
    contacts = ClientContactSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    
    class Meta:
        model = Client
        fields = [
            'id', 'name', 'email', 'phone', 'type', 'document',
            'address', 'city', 'state', 'zip_code', 'company_name',
            'contact_person', 'notes', 'status', 'created_by', 'created_by_name',
            'assigned_to', 'assigned_to_name', 'created_at', 'updated_at', 'last_contact',
            'contacts'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']


class ClientCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = [
            'name', 'email', 'phone', 'type', 'document',
            'address', 'city', 'state', 'zip_code', 'company_name',
            'contact_person', 'notes', 'assigned_to'
        ]

