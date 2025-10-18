from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Client, ClientContact
from .serializers import ClientSerializer, ClientCreateSerializer, ClientContactSerializer, ClientListSerializer
from servicehub.utils.audit import AuditMixin
from servicehub.utils.permissions import IsClientOwnerOrAdmin
from servicehub.utils.filters import ClientFilter


class ClientViewSet(AuditMixin, viewsets.ModelViewSet):
    """
    ViewSet for Client management with audit trail and advanced filtering.
    
    Endpoints:
    - GET /api/v1/clients/ - List all clients
    - POST /api/v1/clients/ - Create a new client
    - GET /api/v1/clients/{id}/ - Retrieve a client
    - PUT /api/v1/clients/{id}/ - Update a client
    - DELETE /api/v1/clients/{id}/ - Soft delete a client
    - POST /api/v1/clients/{id}/restore/ - Restore a deleted client
    - POST /api/v1/clients/{id}/add-contact/ - Add a contact
    - GET /api/v1/clients/{id}/contacts/ - List contacts
    - GET /api/v1/clients/deleted/list/ - List deleted clients
    """
    
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated, IsClientOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ClientFilter
    search_fields = ['name', 'email', 'document', 'company_name', 'phone']
    ordering_fields = ['created_at', 'name', 'status']
    ordering = ['-created_at']
    pagination_class = None  # Use default pagination
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ClientCreateSerializer
        elif self.action == 'list':
            return ClientListSerializer
        return ClientSerializer
    
    def get_permissions(self):
        """Override permissions for specific actions."""
        if self.action in ['create', 'list']:
            return [IsAuthenticated()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        """Create and audit log."""
        serializer.save(created_by=self.request.user)
        super().perform_create(serializer)
    
    @action(detail=True, methods=['post'])
    def add_contact(self, request, pk=None):
        """Add a contact to a client."""
        client = self.get_object()
        serializer = ClientContactSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(client=client)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def contacts(self, request, pk=None):
        """Get all contacts for a client."""
        client = self.get_object()
        contacts = client.contacts.all()
        serializer = ClientContactSerializer(contacts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """Restore a deleted client."""
        try:
            client = Client.all_objects.get(pk=pk)
            client.restore()
            serializer = self.get_serializer(client)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Client.DoesNotExist:
            return Response(
                {'detail': 'Cliente não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def deleted(self, request):
        """List deleted clients."""
        deleted_clients = Client.all_objects.deleted_only()
        serializer = self.get_serializer(deleted_clients, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Get audit history for a client."""
        from servicehub.utils.models import AuditLog
        
        logs = AuditLog.objects.filter(
            model_name='Client',
            object_id=str(pk)
        ).order_by('-created_at')
        
        data = [
            {
                'id': log.id,
                'user': log.user,
                'action': log.get_action_display(),
                'old_values': log.old_values,
                'new_values': log.new_values,
                'created_at': log.created_at,
            }
            for log in logs
        ]
        return Response(data)


class ClientContactViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Client Contacts.
    """
    
    queryset = ClientContact.objects.all()
    serializer_class = ClientContactSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'email', 'phone']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']

