from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Quote, Proposal
from .serializers import QuoteSerializer, QuoteCreateSerializer, ProposalSerializer


class QuoteViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Quote management.
    """
    
    queryset = Quote.objects.all()
    serializer_class = QuoteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'client']
    search_fields = ['quote_number', 'title', 'client__name']
    ordering_fields = ['created_at', 'total']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return QuoteCreateSerializer
        return QuoteSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """Send a quote to the client."""
        quote = self.get_object()
        quote.status = 'sent'
        quote.sent_at = timezone.now()
        quote.save()
        return Response({'detail': 'Orçamento enviado com sucesso.'})
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a quote."""
        quote = self.get_object()
        quote.status = 'approved'
        quote.approved_at = timezone.now()
        quote.save()
        return Response({'detail': 'Orçamento aprovado com sucesso.'})


class ProposalViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Proposal management.
    """
    
    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['proposal_number', 'quote__title']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

