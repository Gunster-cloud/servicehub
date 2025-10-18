from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from .models import Quote, Proposal
from .serializers import (
    QuoteSerializer, QuoteCreateSerializer, ProposalSerializer,
    ProposalCreateSerializer, QuoteListSerializer
)
from servicehub.utils.audit import AuditMixin
from servicehub.utils.permissions import IsClientOwnerOrAdmin
from servicehub.utils.filters import QuoteFilter


class QuoteViewSet(AuditMixin, viewsets.ModelViewSet):
    """
    ViewSet for Quote management with audit trail and advanced filtering.
    
    Endpoints:
    - GET /api/v1/quotes/quotes/ - List all quotes
    - POST /api/v1/quotes/quotes/ - Create a new quote
    - GET /api/v1/quotes/quotes/{id}/ - Retrieve a quote
    - PUT /api/v1/quotes/quotes/{id}/ - Update a quote
    - DELETE /api/v1/quotes/quotes/{id}/ - Soft delete a quote
    - POST /api/v1/quotes/quotes/{id}/send/ - Send a quote
    - POST /api/v1/quotes/quotes/{id}/approve/ - Approve a quote
    - POST /api/v1/quotes/quotes/{id}/reject/ - Reject a quote
    - POST /api/v1/quotes/quotes/{id}/restore/ - Restore a deleted quote
    - GET /api/v1/quotes/quotes/{id}/history/ - Get audit history
    """
    
    queryset = Quote.objects.all()
    serializer_class = QuoteSerializer
    permission_classes = [IsAuthenticated, IsClientOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = QuoteFilter
    search_fields = ['quote_number', 'title', 'client__name']
    ordering_fields = ['created_at', 'total', 'status']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return QuoteCreateSerializer
        elif self.action == 'list':
            return QuoteListSerializer
        return QuoteSerializer
    
    def perform_create(self, serializer):
        """Create and audit log."""
        serializer.save(created_by=self.request.user)
        super().perform_create(serializer)
    
    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """Send a quote to the client."""
        quote = self.get_object()
        quote.status = 'sent'
        quote.sent_at = timezone.now()
        quote.save()
        
        super().perform_update(self.get_serializer(quote, data={}))
        
        return Response(
            {'detail': 'Orçamento enviado com sucesso.'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a quote."""
        quote = self.get_object()
        quote.status = 'approved'
        quote.approved_at = timezone.now()
        quote.save()
        
        return Response(
            {'detail': 'Orçamento aprovado com sucesso.'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a quote."""
        quote = self.get_object()
        quote.status = 'rejected'
        quote.save()
        
        return Response(
            {'detail': 'Orçamento rejeitado.'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """Restore a deleted quote."""
        try:
            quote = Quote.all_objects.get(pk=pk)
            quote.restore()
            serializer = self.get_serializer(quote)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Quote.DoesNotExist:
            return Response(
                {'detail': 'Orçamento não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Get audit history for a quote."""
        from servicehub.utils.models import AuditLog
        
        logs = AuditLog.objects.filter(
            model_name='Quote',
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


class ProposalViewSet(AuditMixin, viewsets.ModelViewSet):
    """
    ViewSet for Proposal management with audit trail.
    """
    
    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['proposal_number', 'quote__title']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ProposalCreateSerializer
        return ProposalSerializer
    
    def perform_create(self, serializer):
        """Create and audit log."""
        serializer.save()
        super().perform_create(serializer)
    
    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """Send a proposal."""
        proposal = self.get_object()
        proposal.status = 'sent'
        proposal.sent_at = timezone.now()
        proposal.save()
        
        return Response(
            {'detail': 'Proposta enviada com sucesso.'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Accept a proposal."""
        proposal = self.get_object()
        proposal.status = 'accepted'
        proposal.accepted_at = timezone.now()
        proposal.save()
        
        return Response(
            {'detail': 'Proposta aceita com sucesso.'},
            status=status.HTTP_200_OK
        )

